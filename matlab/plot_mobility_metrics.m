function plot_mobility_metrics(outputRoot)
%PLOT_MOBILITY_METRICS Plot synthetic smart-city mobility metrics.
% Usage:
%   addpath('matlab')
%   plot_mobility_metrics('outputs')

if nargin < 1
    outputRoot = 'outputs';
end

resultsDir = fullfile(outputRoot, 'results');
figuresDir = fullfile(outputRoot, 'figures');
if ~exist(figuresDir, 'dir')
    mkdir(figuresDir);
end

comparisonPath = fullfile(resultsDir, 'synthetic_scenario_comparison.csv');
riskPath = fullfile(resultsDir, 'synthetic_congestion_accident_risk.csv');

if exist(comparisonPath, 'file')
    comparison = readtable(comparisonPath);
    figure('Name', 'Scenario Planning Score');
    bar(categorical(comparison.scenario), comparison.planning_score);
    ylabel('Planning score');
    title('Synthetic mobility planning score by scenario');
    grid on;
    saveas(gcf, fullfile(figuresDir, 'matlab_scenario_planning_score.png'));
end

if exist(riskPath, 'file')
    risk = readtable(riskPath);
    figure('Name', 'Congestion vs Accident Risk');
    scatter(risk.congestion_score, risk.accident_risk_score, 28, 'filled');
    xlabel('Congestion score');
    ylabel('Accident-risk score');
    title('Synthetic road-segment congestion and accident risk');
    grid on;
    saveas(gcf, fullfile(figuresDir, 'matlab_congestion_accident_scatter.png'));
end
end
