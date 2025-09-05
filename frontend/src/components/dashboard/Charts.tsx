import { LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

interface ChartData {
  name: string;
  value: number;
  [key: string]: string | number;
}

// Line Chart Component
interface LineChartProps {
  data: ChartData[];
  dataKey?: string;
  height?: number;
  color?: string;
  showGrid?: boolean;
}

export function SimpleLineChart({ 
  data, 
  dataKey = 'value', 
  height = 300, 
  color = '#6C63FF',
  showGrid = true 
}: LineChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        {showGrid && <CartesianGrid strokeDasharray="3 3" className="opacity-30" />}
        <XAxis 
          dataKey="name" 
          className="text-xs text-muted-600 dark:text-muted-400"
          axisLine={false}
          tickLine={false}
        />
        <YAxis 
          className="text-xs text-muted-600 dark:text-muted-400"
          axisLine={false}
          tickLine={false}
        />
        <Tooltip 
          contentStyle={{ 
            backgroundColor: 'var(--tooltip-bg, #ffffff)',
            border: '1px solid var(--tooltip-border, #e5e7eb)',
            borderRadius: '12px',
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
          }}
          labelStyle={{ color: 'var(--tooltip-text, #374151)' }}
        />
        <Line 
          type="monotone" 
          dataKey={dataKey} 
          stroke={color} 
          strokeWidth={3}
          dot={{ fill: color, strokeWidth: 2, r: 4 }}
          activeDot={{ r: 6, stroke: color, strokeWidth: 2 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

// Area Chart Component
interface AreaChartProps extends LineChartProps {
  fillOpacity?: number;
}

export function SimpleAreaChart({ 
  data, 
  dataKey = 'value', 
  height = 300, 
  color = '#6C63FF',
  showGrid = true,
  fillOpacity = 0.3
}: AreaChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        {showGrid && <CartesianGrid strokeDasharray="3 3" className="opacity-30" />}
        <XAxis 
          dataKey="name" 
          className="text-xs text-muted-600 dark:text-muted-400"
          axisLine={false}
          tickLine={false}
        />
        <YAxis 
          className="text-xs text-muted-600 dark:text-muted-400"
          axisLine={false}
          tickLine={false}
        />
        <Tooltip 
          contentStyle={{ 
            backgroundColor: 'var(--tooltip-bg, #ffffff)',
            border: '1px solid var(--tooltip-border, #e5e7eb)',
            borderRadius: '12px',
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
          }}
        />
        <Area 
          type="monotone" 
          dataKey={dataKey} 
          stroke={color} 
          fill={color}
          fillOpacity={fillOpacity}
          strokeWidth={2}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

// Bar Chart Component
interface BarChartProps {
  data: ChartData[];
  dataKey?: string;
  height?: number;
  color?: string;
  showGrid?: boolean;
  horizontal?: boolean;
}

export function SimpleBarChart({ 
  data, 
  dataKey = 'value', 
  height = 300, 
  color = '#6C63FF',
  showGrid = true,
  horizontal = false
}: BarChartProps) {
  const ChartComponent = BarChart;
  
  return (
    <ResponsiveContainer width="100%" height={height}>
      <ChartComponent 
        data={data} 
        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        layout={horizontal ? 'horizontal' : 'vertical'}
      >
        {showGrid && <CartesianGrid strokeDasharray="3 3" className="opacity-30" />}
        {horizontal ? (
          <>
            <XAxis type="number" className="text-xs text-muted-600 dark:text-muted-400" axisLine={false} tickLine={false} />
            <YAxis type="category" dataKey="name" className="text-xs text-muted-600 dark:text-muted-400" axisLine={false} tickLine={false} />
          </>
        ) : (
          <>
            <XAxis dataKey="name" className="text-xs text-muted-600 dark:text-muted-400" axisLine={false} tickLine={false} />
            <YAxis className="text-xs text-muted-600 dark:text-muted-400" axisLine={false} tickLine={false} />
          </>
        )}
        <Tooltip 
          contentStyle={{ 
            backgroundColor: 'var(--tooltip-bg, #ffffff)',
            border: '1px solid var(--tooltip-border, #e5e7eb)',
            borderRadius: '12px',
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
          }}
        />
        <Bar 
          dataKey={dataKey} 
          fill={color} 
          radius={[4, 4, 0, 0]}
        />
      </ChartComponent>
    </ResponsiveContainer>
  );
}

// Pie Chart Component
interface PieChartProps {
  data: ChartData[];
  height?: number;
  colors?: string[];
  showLabels?: boolean;
  showLegend?: boolean;
}

const DEFAULT_COLORS = ['#6C63FF', '#22C55E', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4'];

export function SimplePieChart({ 
  data, 
  height = 300, 
  colors = DEFAULT_COLORS,
  showLabels = false,
  showLegend = true
}: PieChartProps) {
  const renderLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }: any) => {
    const RADIAN = Math.PI / 180;
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    return (
      <text 
        x={x} 
        y={y} 
        fill="white" 
        textAnchor={x > cx ? 'start' : 'end'} 
        dominantBaseline="central"
        className="text-xs font-medium"
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };

  return (
    <ResponsiveContainer width="100%" height={height}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={showLabels ? renderLabel : false}
          outerRadius={80}
          fill="#8884d8"
          dataKey="value"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
          ))}
        </Pie>
        <Tooltip 
          contentStyle={{ 
            backgroundColor: 'var(--tooltip-bg, #ffffff)',
            border: '1px solid var(--tooltip-border, #e5e7eb)',
            borderRadius: '12px',
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
          }}
        />
        {showLegend && (
          <Legend 
            wrapperStyle={{ paddingTop: '20px' }}
            iconType="circle"
          />
        )}
      </PieChart>
    </ResponsiveContainer>
  );
}