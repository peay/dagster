import {QueryResult} from '@apollo/client';
import {Box, Tabs} from '@dagster-io/ui';
import * as React from 'react';

import {QueryRefreshCountdown, QueryRefreshState} from '../app/QueryRefresh';
import {TabLink} from '../ui/TabLink';

import {useCanSeeConfig} from './useCanSeeConfig';

interface Props<TData> {
  refreshState: QueryRefreshState;
  queryData?: QueryResult<TData, any>;
  tab: string;
}

export const InstanceTabContext = React.createContext({healthTitle: 'Daemons'});

export const InstanceTabs = <TData extends Record<string, any>>(props: Props<TData>) => {
  const {healthTitle} = React.useContext(InstanceTabContext);
  const {refreshState, tab} = props;
  const canSeeConfig = useCanSeeConfig();

  return (
    <Box flex={{direction: 'row', justifyContent: 'space-between', alignItems: 'flex-end'}}>
      <Tabs selectedTabId={tab}>
        <TabLink id="overview" title="Overview" to="/instance/overview" />
        <TabLink id="health" title={healthTitle} to="/instance/health" />
        <TabLink id="schedules" title="Schedules" to="/instance/schedules" />
        <TabLink id="sensors" title="Sensors" to="/instance/sensors" />
        <TabLink id="backfills" title="Backfills" to="/instance/backfills" />
        {canSeeConfig ? <TabLink id="config" title="Configuration" to="/instance/config" /> : null}
      </Tabs>
      {refreshState ? (
        <Box padding={{bottom: 8}}>
          <QueryRefreshCountdown refreshState={refreshState} />
        </Box>
      ) : null}
    </Box>
  );
};
