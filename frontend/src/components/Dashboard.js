import React from 'react';
import ContentArchitect from './ContentArchitect';
import AdvancedAssessor from './AdvancedAssessor';
import PersonalizationEngine from './PersonalizationEngine';
import SummarizationSuite from './SummarizationSuite';
import MultimediaStudio from './MultimediaStudio';
import SmartLocalizer from './SmartLocalizer';

const Dashboard = () => {
  return (
    <div className="dashboard-grid">
      <ContentArchitect />
      <AdvancedAssessor />
      <PersonalizationEngine />
      <SummarizationSuite />
      <SmartLocalizer />
      <MultimediaStudio />
    </div>
  );
};

export default Dashboard;
