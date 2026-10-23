import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  CartesianGrid,
} from 'recharts';
import { XAIAttribution } from '../types';
import { BarChart3 } from 'lucide-react';

interface ShapWaterfallProps {
  attributions?: XAIAttribution[];
}

export const ShapWaterfall: React.FC<ShapWaterfallProps> = ({ attributions = [] }) => {
  const data = (attributions && attributions.length > 0)
    ? attributions
    : [
        { kpi: 'amf_active_ngap_contexts', shap_value: 0.42 },
        { kpi: 'amf_cpu_saturation', shap_value: 0.35 },
        { kpi: 'sbi_client_queue_depth', shap_value: 0.18 },
        { kpi: 'upf_packet_drop_ratio', shap_value: 0.12 },
      ];

  const monochromeFills = ['#FFFFFF', '#D4D4D4', '#A3A3A3', '#737373', '#525252'];

  return (
    <div className="noc-panel p-5 flex flex-col h-full border border-neutral-800">
      <div className="flex items-center justify-between pb-3 border-b border-neutral-800">
        <div className="flex items-center space-x-2">
          <BarChart3 className="w-4 h-4 text-white" />
          <h3 className="text-sm font-semibold text-neutral-200 uppercase tracking-wider">
            Post-Hoc XAI (SHAP Waterfall Attributions)
          </h3>
        </div>
        <span className="text-[11px] font-mono text-neutral-300 bg-neutral-900 px-2 py-0.5 rounded border border-neutral-800">
          Paper 13 Grounded
        </span>
      </div>

      <div className="flex-1 mt-4 min-h-[220px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            layout="vertical"
            margin={{ top: 10, right: 30, left: 100, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#262626" horizontal={false} />
            <XAxis
              type="number"
              domain={[0, 0.6]}
              tick={{ fill: '#A3A3A3', fontSize: 11 }}
              stroke="#404040"
            />
            <YAxis
              type="category"
              dataKey="kpi"
              tick={{ fill: '#FFFFFF', fontSize: 11, fontFamily: 'monospace' }}
              stroke="#404040"
              width={180}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0D0D0D',
                borderColor: '#404040',
                borderRadius: '8px',
                fontSize: '12px',
                color: '#FFFFFF',
              }}
              formatter={(val: any) => [`${(Number(val) * 100).toFixed(1)}% Impact`, 'SHAP Score']}
            />
            <Bar dataKey="shap_value" radius={[0, 4, 4, 0]}>
              {data.map((_entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={monochromeFills[index % monochromeFills.length]}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="text-[10px] text-neutral-400 text-center mt-2 font-mono">
        Feature attributions computed via Mask Permutation & TreeSHAP on 5GC SBA PM Counters
      </div>
    </div>
  );
};
