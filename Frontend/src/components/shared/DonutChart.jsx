import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

const COLORS = ['#14B8A6', '#0F172A', '#64748B'];

const DonutChart = ({ data, total, centerLabel = 'Total' }) => {
  return (
    <div className="flex flex-col items-center">
      <div className="relative w-48 h-48">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={55}
              outerRadius={80}
              dataKey="value"
              stroke="none"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        {/* Center label */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-bold text-primary">{total}</span>
          <span className="text-xs text-secondary">{centerLabel}</span>
        </div>
      </div>
      {/* Legend */}
      <div className="flex flex-wrap gap-4 mt-4 justify-center">
        {data.map((entry, index) => (
          <div key={index} className="flex items-center gap-2">
            <span
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: COLORS[index % COLORS.length] }}
            />
            <span className="text-xs text-secondary">{entry.name}</span>
            <span className="text-xs font-medium text-primary">{entry.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DonutChart;
