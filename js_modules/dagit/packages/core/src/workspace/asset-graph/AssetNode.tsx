import {gql} from '@apollo/client';
import {ContextMenu2 as ContextMenu} from '@blueprintjs/popover2';
import {
  ColorsWIP,
  IconWIP,
  markdownToPlaintext,
  MenuItemWIP,
  MenuWIP,
  Spinner,
  Tooltip,
  FontFamily,
  MenuLink,
  Box,
} from '@dagster-io/ui';
import {isEqual} from 'lodash';
import React from 'react';
import styled from 'styled-components/macro';

import {displayNameForAssetKey, withMiddleTruncation} from '../../app/Util';
import {LATEST_MATERIALIZATION_METADATA_FRAGMENT} from '../../assets/LastMaterializationMetadata';
import {NodeHighlightColors} from '../../graph/OpNode';
import {OpTags} from '../../graph/OpTags';
import {METADATA_ENTRY_FRAGMENT} from '../../metadata/MetadataEntry';
import {TimeElapsed} from '../../runs/TimeElapsed';
import {TimestampDisplay} from '../../schedules/TimestampDisplay';
import {buildRepoAddress} from '../buildRepoAddress';

import {LiveDataForNode, __ASSET_GROUP} from './Utils';
import {AssetNodeFragment} from './types/AssetNodeFragment';
import {useLaunchSingleAssetJob} from './useLaunchSingleAssetJob';

const MAX_ANONTATIONS_WIDTH = 85;
const DISPLAY_NAME_MAX_LENGTH = 50;
const DISPLAY_NAME_PX_PER_CHAR = 8.0;

export const AssetNode: React.FC<{
  definition: AssetNodeFragment;
  liveData?: LiveDataForNode;
  metadata: {key: string; value: string}[];
  selected: boolean;
  jobName: string;
  inAssetCatalog?: boolean;
}> = React.memo(({definition, metadata, selected, liveData, jobName, inAssetCatalog}) => {
  const launch = useLaunchSingleAssetJob();

  const event = liveData?.lastMaterialization;
  const kind = metadata.find((m) => m.key === 'kind')?.value;
  const repoAddress = buildRepoAddress(
    definition.repository.name,
    definition.repository.location.name,
  );

  const displayName = withMiddleTruncation(displayNameForAssetKey(definition.assetKey), {
    maxLength: DISPLAY_NAME_MAX_LENGTH,
  });

  return (
    <ContextMenu
      content={
        <MenuWIP>
          <MenuItemWIP
            icon="materialization"
            onClick={(e) => {
              launch(repoAddress, jobName, definition.opName);
              e.stopPropagation();
            }}
            text={
              <span>
                {event ? 'Rematerialize ' : 'Materialize '}
                <span style={{fontFamily: 'monospace', fontWeight: 600}}>{displayName}</span>
              </span>
            }
          />
          {!inAssetCatalog && (
            <MenuLink
              icon="link"
              to={`/instance/assets/${definition.assetKey.path.join('/')}`}
              onClick={(e) => e.stopPropagation()}
              text="View in Asset Catalog"
            />
          )}
        </MenuWIP>
      }
    >
      <AssetNodeContainer $selected={selected}>
        <AssetNodeBox>
          <Name>
            <span style={{marginTop: 1}}>
              <IconWIP name="asset" />
            </span>
            <div style={{overflow: 'hidden', textOverflow: 'ellipsis', marginTop: -1}}>
              {displayName}
            </div>
            <div style={{flex: 1}} />
            <div style={{display: 'flex', gap: 4, maxWidth: MAX_ANONTATIONS_WIDTH}}>
              {liveData && liveData.inProgressRunIds.length > 0 ? (
                <Tooltip content="A run is currently rematerializing this asset.">
                  <Spinner purpose="body-text" />
                </Tooltip>
              ) : liveData && liveData.unstartedRunIds.length > 0 ? (
                <Tooltip content="A run has started that will rematerialize this asset soon.">
                  <Spinner purpose="body-text" stopped />
                </Tooltip>
              ) : liveData &&
                (liveData.runWhichFailedToMaterialize || liveData.runsSinceMaterialization) ? (
                <Tooltip content="This asset was not materialized by one or more recent runs.">
                  <IconWIP name="warning" color={ColorsWIP.Gray400} />
                </Tooltip>
              ) : undefined}

              {liveData?.computeStatus === 'old' && (
                <UpstreamNotice>
                  upstream
                  <br />
                  changed
                </UpstreamNotice>
              )}
            </div>
          </Name>
          {definition.description && !inAssetCatalog && (
            <Description>{markdownToPlaintext(definition.description).split('\n')[0]}</Description>
          )}
          <Stats>
            {event ? (
              <>
                <StatsRow>
                  {event.stepStats.endTime ? (
                    <TimestampDisplay
                      timestamp={event.stepStats.endTime}
                      timeFormat={{showSeconds: false, showTimezone: false}}
                    />
                  ) : (
                    'Never'
                  )}
                  <TimeElapsed
                    startUnix={event.stepStats.startTime}
                    endUnix={event.stepStats.endTime}
                  />
                </StatsRow>
              </>
            ) : (
              <>
                <StatsRow style={{opacity: 0.5}}>
                  <span>No materializations</span>
                  <span>—</span>
                </StatsRow>
              </>
            )}
            {definition.opName && displayName !== definition.opName && (
              <StatsRow>
                <Box
                  flex={{gap: 4, alignItems: 'flex-end'}}
                  style={{marginLeft: -2, overflow: 'hidden'}}
                >
                  <IconWIP name="op" size={16} />
                  <div
                    style={{
                      minWidth: 0,
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                    }}
                  >
                    {definition.opName}
                  </div>
                </Box>
              </StatsRow>
            )}
          </Stats>
          {kind && (
            <OpTags
              minified={false}
              style={{right: -2, paddingTop: 5}}
              tags={[
                {
                  label: kind,
                  onClick: () => {
                    window.requestAnimationFrame(() =>
                      document.dispatchEvent(new Event('show-kind-info')),
                    );
                  },
                },
              ]}
            />
          )}
        </AssetNodeBox>
      </AssetNodeContainer>
    </ContextMenu>
  );
}, isEqual);

export const ASSET_NODE_LIVE_FRAGMENT = gql`
  fragment AssetNodeLiveFragment on AssetNode {
    id
    opName
    repository {
      id
      name
      location {
        id
        name
      }
    }
    assetKey {
      path
    }
    assetMaterializations(limit: 1) {
      ...LatestMaterializationMetadataFragment

      metadataEntries {
        ...MetadataEntryFragment
      }
      stepStats {
        stepKey
        startTime
        endTime
      }
    }
  }

  ${METADATA_ENTRY_FRAGMENT}
  ${LATEST_MATERIALIZATION_METADATA_FRAGMENT}
`;

export const ASSET_NODE_FRAGMENT = gql`
  fragment AssetNodeFragment on AssetNode {
    id
    opName
    description
    metadataEntries {
      ...MetadataEntryFragment
    }
    partitionDefinition
    assetKey {
      path
    }
    repository {
      id
      name
      location {
        id
        name
      }
    }
  }
  ${METADATA_ENTRY_FRAGMENT}
`;

export const getNodeDimensions = (def: {
  assetKey: {path: string[]};
  opName: string | null;
  description?: string | null;
}) => {
  let height = 75;
  if (def.description) {
    height += 25;
  }
  const displayName = displayNameForAssetKey(def.assetKey);
  if (def.opName && displayName !== def.opName) {
    height += 25;
  }
  return {
    width:
      Math.max(
        200,
        Math.min(DISPLAY_NAME_MAX_LENGTH, displayName.length) * DISPLAY_NAME_PX_PER_CHAR,
      ) + MAX_ANONTATIONS_WIDTH,
    height,
  };
};

const BoxColors = {
  Divider: 'rgba(219, 219, 244, 1)',
  Description: 'rgba(245, 245, 250, 1)',
  Stats: 'rgba(236, 236, 248, 1)',
};

const AssetNodeContainer = styled.div<{$selected: boolean}>`
  outline: ${(p) => (p.$selected ? `2px dashed ${NodeHighlightColors.Border}` : 'none')};
  border-radius: 6px;
  outline-offset: -1px;
  padding: 4px;
  margin-top: 10px;
  margin-right: 4px;
  margin-left: 4px;
  margin-bottom: 2px;
  background: ${(p) => (p.$selected ? NodeHighlightColors.Background : 'white')};
  inset: 0;
`;

const AssetNodeBox = styled.div`
  border: 2px solid ${ColorsWIP.Blue200};
  background: ${ColorsWIP.White};
  border-radius: 5px;
  position: relative;
  &:hover {
    box-shadow: ${ColorsWIP.Blue200} inset 0px 0px 0px 1px, rgba(0, 0, 0, 0.12) 0px 2px 12px 0px;
  }
`;

const Name = styled.div`
  /** Keep in sync with DISPLAY_NAME_PX_PER_CHAR */
  display: flex;
  padding: 4px 6px;
  background: ${ColorsWIP.White};
  font-family: ${FontFamily.monospace};
  border-top-left-radius: 5px;
  border-top-right-radius: 5px;
  font-weight: 600;
  gap: 4px;
`;

const Description = styled.div`
  background: ${BoxColors.Description};
  padding: 4px 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  border-top: 1px solid ${BoxColors.Divider};
  font-size: 12px;
`;

const Stats = styled.div`
  background: ${BoxColors.Stats};
  padding: 4px 8px;
  border-top: 1px solid ${BoxColors.Divider};
  font-size: 12px;
  line-height: 18px;
`;

const StatsRow = styled.div`
  display: flex;
  justify-content: space-between;
  min-height: 14px;
`;

const UpstreamNotice = styled.div`
  background: ${ColorsWIP.Yellow200};
  color: ${ColorsWIP.Yellow700};
  line-height: 10px;
  font-size: 11px;
  text-align: right;
  margin-top: -4px;
  margin-bottom: -4px;
  padding: 2.5px 5px;
  margin-right: -6px;
  border-top-right-radius: 3px;
`;
