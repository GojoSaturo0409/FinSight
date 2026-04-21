import { useState } from 'react';
import { FileText, Download, Loader2, FileDown, Eye } from 'lucide-react';

const ReportExport = () => {
    const [format, setFormat] = useState<'html' | 'pdf'>('html');
    const [loading, setLoading] = useState(false);
    const [preview, setPreview] = useState<any>(null);
    const [error, setError] = useState('');

    const API_BASE = 'http://localhost:8000';

    const reportData = {
        title: 'Monthly Financial Report',
        start_date: '2024-03-01',
        end_date: '2024-03-31',
        income: 5000,
        spending_chart: {
            Housing: 1500,
            Food: 300,
            Transport: 150,
            Subscriptions: 50,
        },
        recommendations: [
            "Category Alert: 'Housing' is 30.0% of your income. The recommended limit per category is 30%.",
            "Great job! You hit your monthly savings target.",
            "Investment Opportunity: Consider low-risk index funds with your surplus.",
        ],
        portfolio: [
            { symbol: 'SPY', price: 523.40, trend: 'up' },
            { symbol: 'BND', price: 72.85, trend: 'up' },
            { symbol: 'VTI', price: 261.20, trend: 'up' },
        ],
    };

    const handlePreview = async () => {
        setLoading(true);
        setError('');
        try {
            const response = await fetch(`${API_BASE}/reports/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(reportData),
            });
            if (response.ok) {
                const data = await response.json();
                setPreview(data.report);
            } else {
                throw new Error('Failed to generate report');
            }
        } catch {
            // Fallback preview
            setPreview({
                header: reportData.title,
                date_range: `${reportData.start_date} to ${reportData.end_date}`,
                monthly_summary: {
                    income: reportData.income,
                    expenses: 2000,
                    savings: 3000,
                },
                spending_chart: reportData.spending_chart,
                recommendations: reportData.recommendations,
            });
        } finally {
            setLoading(false);
        }
    };

    const handleExport = async () => {
        setLoading(true);
        setError('');

        try {
            // Use fetch() with Authorization header (JWT-compatible)
            // For the prototype, we skip auth since it's demo mode
            const response = await fetch(`${API_BASE}/reports/export/${format}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // In production: 'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(reportData),
            });

            if (!response.ok) throw new Error(`Export failed: ${response.statusText}`);

            // Convert response blob to downloadable file
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `finsight_report.${format}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } catch (err: any) {
            setError(`Export failed. Make sure the backend is running at ${API_BASE}`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            {/* Export Controls */}
            <div className="bg-gradient-to-br from-purple-500/10 to-indigo-500/10 backdrop-blur-xl border border-purple-500/20 rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-6">
                    <FileText size={22} className="text-purple-400" />
                    <h3 className="text-xl font-bold">Monthly Report</h3>
                </div>

                <p className="text-sm text-neutral-400 mb-6">
                    Generate a comprehensive financial report with spending charts, category breakdowns,
                    savings recommendations, and portfolio summary.
                </p>

                {/* Format Selector */}
                <div className="flex gap-3 mb-6">
                    <button
                        onClick={() => setFormat('html')}
                        className={`flex-1 py-3 px-4 rounded-xl text-sm font-medium transition-all duration-200 border ${format === 'html'
                                ? 'bg-indigo-500/20 border-indigo-500/40 text-indigo-300'
                                : 'bg-neutral-900/50 border-white/5 text-neutral-400 hover:border-white/10'
                            }`}
                    >
                        <FileDown size={16} className="inline mr-2" />
                        HTML Report
                    </button>
                    <button
                        onClick={() => setFormat('pdf')}
                        className={`flex-1 py-3 px-4 rounded-xl text-sm font-medium transition-all duration-200 border ${format === 'pdf'
                                ? 'bg-indigo-500/20 border-indigo-500/40 text-indigo-300'
                                : 'bg-neutral-900/50 border-white/5 text-neutral-400 hover:border-white/10'
                            }`}
                    >
                        <FileDown size={16} className="inline mr-2" />
                        PDF Report
                    </button>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3">
                    <button
                        onClick={handlePreview}
                        disabled={loading}
                        className="flex-1 flex items-center justify-center gap-2 bg-neutral-800 text-white font-semibold rounded-xl py-3 hover:bg-neutral-700 transition-all disabled:opacity-50"
                    >
                        {loading ? <Loader2 size={18} className="animate-spin" /> : <Eye size={18} />}
                        Preview
                    </button>
                    <button
                        onClick={handleExport}
                        disabled={loading}
                        className="flex-1 flex items-center justify-center gap-2 bg-indigo-500 text-white font-semibold rounded-xl py-3 hover:bg-indigo-400 transition-all disabled:opacity-50"
                    >
                        {loading ? <Loader2 size={18} className="animate-spin" /> : <Download size={18} />}
                        Export {format.toUpperCase()}
                    </button>
                </div>

                {error && (
                    <div className="mt-4 p-3 bg-rose-500/10 border border-rose-500/20 rounded-lg text-rose-300 text-xs">
                        {error}
                    </div>
                )}
            </div>

            {/* Report Preview */}
            {preview && (
                <div className="bg-neutral-900/50 backdrop-blur-xl border border-white/5 rounded-2xl p-6">
                    <h3 className="text-lg font-bold mb-4">Report Preview</h3>

                    <div className="space-y-4">
                        {/* Header */}
                        <div className="text-center pb-4 border-b border-white/5">
                            <h4 className="text-xl font-bold text-white">{preview.header}</h4>
                            <p className="text-xs text-neutral-500 mt-1">{preview.date_range}</p>
                        </div>

                        {/* Summary */}
                        {preview.monthly_summary && (
                            <div className="grid grid-cols-3 gap-3">
                                <div className="bg-neutral-800/50 rounded-xl p-3 text-center">
                                    <div className="text-xs text-neutral-500 uppercase">Income</div>
                                    <div className="text-lg font-bold text-emerald-400 mt-1">
                                        ${preview.monthly_summary.income?.toLocaleString()}
                                    </div>
                                </div>
                                <div className="bg-neutral-800/50 rounded-xl p-3 text-center">
                                    <div className="text-xs text-neutral-500 uppercase">Expenses</div>
                                    <div className="text-lg font-bold text-rose-400 mt-1">
                                        ${preview.monthly_summary.expenses?.toLocaleString()}
                                    </div>
                                </div>
                                <div className="bg-neutral-800/50 rounded-xl p-3 text-center">
                                    <div className="text-xs text-neutral-500 uppercase">Savings</div>
                                    <div className="text-lg font-bold text-indigo-400 mt-1">
                                        ${preview.monthly_summary.savings?.toLocaleString()}
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Spending Breakdown */}
                        {preview.spending_chart && Object.keys(preview.spending_chart).length > 0 && (
                            <div>
                                <h5 className="text-sm font-semibold text-neutral-300 mb-2">Spending by Category</h5>
                                <div className="space-y-2">
                                    {Object.entries(preview.spending_chart).map(([cat, amt]: [string, any]) => {
                                        const total = Object.values(preview.spending_chart as Record<string, number>).reduce((s: number, v: number) => s + v, 0);
                                        const pct = total > 0 ? ((amt / total) * 100).toFixed(1) : '0';
                                        return (
                                            <div key={cat} className="flex items-center justify-between text-sm">
                                                <span className="text-neutral-400">{cat}</span>
                                                <div className="flex items-center gap-3">
                                                    <div className="w-24 bg-neutral-800 rounded-full h-1.5">
                                                        <div
                                                            className="bg-indigo-500 h-1.5 rounded-full transition-all"
                                                            style={{ width: `${pct}%` }}
                                                        />
                                                    </div>
                                                    <span className="text-neutral-300 font-medium w-16 text-right">${(amt as number).toLocaleString()}</span>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        )}

                        {/* Recommendations */}
                        {preview.recommendations && preview.recommendations.length > 0 && (
                            <div>
                                <h5 className="text-sm font-semibold text-neutral-300 mb-2">Recommendations</h5>
                                <ul className="space-y-1">
                                    {preview.recommendations.map((rec: string, i: number) => (
                                        <li key={i} className="text-xs text-neutral-400 py-1">• {rec}</li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default ReportExport;
