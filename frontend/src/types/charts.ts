// Chart Component Types

export interface ChartData {
  name: string;
  value: number;
  [key: string]: string | number;
}

export interface PieChartLabelProps {
  cx: number;
  cy: number;
  midAngle?: number;
  innerRadius: number;
  outerRadius: number;
  percent?: number;
  index?: number;
}

export interface LineChartProps {
  data: ChartData[];
  dataKey?: string;
  height?: number;
  color?: string;
  showGrid?: boolean;
}

export interface AreaChartProps extends LineChartProps {
  fillOpacity?: number;
}

export interface BarChartProps {
  data: ChartData[];
  dataKey?: string;
  height?: number;
  color?: string;
  showGrid?: boolean;
  horizontal?: boolean;
}

export interface PieChartProps {
  data: ChartData[];
  height?: number;
  colors?: string[];
  showLabels?: boolean;
  showLegend?: boolean;
}
