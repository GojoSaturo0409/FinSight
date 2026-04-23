import { useState, useEffect } from 'react';
import { AlertTriangle, Lightbulb, CheckCircle, Zap } from 'lucide-react';
import { apiFetch } from '../api';

interface Recommendation {
    text: string;
    type: 'warning' | 'tip' | 'success';
}

const RecommendationsPanel = () => {
    const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
    const [loading, setLoading] = useState(true);

    const classifyRecommendation = (text: string): 'warning' | 'tip' | 'success' => {
        const lower = text.toLowerCase();
        if (lower.includes('alert') || lower.includes('exceeding') || lower.includes('warning') || lower.includes('over')) return 'warning';
        if (lower.includes('great') || lower.includes('success') || lower.includes('met') || lower.includes('achieved')) return 'success';
        return 'tip';
    };

    const generateRecommendations = async () => {
        setLoading(true);

        try {
            const autoData = await apiFetch('/recommendations/generate-auto');
            if (autoData.recommendations && autoData.recommendations.length > 0) {
                const recs = autoData.recommendations.map((r: string) => ({
                    text: r,
                    type: classifyRecommendation(r),
                }));
                setRecommendations(recs);
                setLoading(false);
                return;
            }
        } catch {
            // next try building it from /transactions/all
        }

        try {
            const txData = await apiFetch('/ingestion/transactions/all');
            const transactions = txData.data || [];

            const categoryTotals: Record<string, number> = {};
            const merchantCounts: Record<string, number> = {};
            let totalSpend = 0;

            for (const tx of transactions) {
                if (tx.category === 'Income') continue;
                const cat = tx.category || 'Uncategorized';
                categoryTotals[cat] = (categoryTotals[cat] || 0) + tx.amount;
                totalSpend += tx.amount;

                const merchant = tx.merchant || 'Unknown';
                merchantCounts[merchant] = (merchantCounts[merchant] || 0) + 1;
            }

            const recurring = Object.entries(merchantCounts)
                .filter(([, count]) => count >= 2)
                .map(([name]) => name);

            const realContext = {
                monthly_income: 5000,
                monthly_spend: totalSpend,
                savings_target: 1500,
                categories: categoryTotals,
                recurring_merchants: recurring,
            };

            const response = await apiFetch('/recommendations/generate', {
                method: 'POST',
                body: JSON.stringify(realContext),
            });

            if (response.recommendations && response.recommendations.length > 0) {
                const recs = response.recommendations.map((r: string) => ({
                    text: r,
                    type: classifyRecommendation(r),
                }));
                setRecommendations(recs);
            } else {
                throw new Error('API unavailable');
            }
        } catch {
            setRecommendations([]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        generateRecommendations();
    }, []);

    const getTypeStyles = (type: string) => {
        switch (type) {
            case 'warning': return { bg: 'bg-rose-500/10', border: 'border-rose-500/20', icon: <AlertTriangle size={20} className="text-rose-400" /> };
            case 'success': return { bg: 'bg-emerald-500/10', border: 'border-emerald-500/20', icon: <CheckCircle size={20} className="text-emerald-400" /> };
            default: return { bg: 'bg-amber-500/10', border: 'border-amber-500/20', icon: <Lightbulb size={20} className="text-amber-400" /> };
        }
    };

    return (
        <div className="bg-neutral-900/50 backdrop-blur-xl border border-white/5 rounded-2xl p-6">
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-purple-500/10 flex items-center justify-center border border-purple-500/20">
                        <Zap size={20} className="text-purple-400" />
                    </div>
                    <h3 className="text-xl font-bold">AI Financial Insights</h3>
                </div>
                <button
                    onClick={generateRecommendations}
                    disabled={loading}
                    className="text-xs bg-neutral-800 text-neutral-300 px-3 py-1.5 rounded-lg border border-white/5 hover:border-white/10 hover:bg-neutral-700 transition-all disabled:opacity-50"
                >
                    {loading ? 'Analyzing...' : 'Refresh Insights'}
                </button>
            </div>

            {loading ? (
                <div className="py-12 flex justify-center">
                    <div className="w-6 h-6 border-2 border-purple-500/30 border-t-purple-500 rounded-full animate-spin" />
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {recommendations.map((rec, idx) => {
                        const styles = getTypeStyles(rec.type);
                        return (
                            <div key={idx} className={`${styles.bg} ${styles.border} border rounded-xl p-5 flex gap-4 transition-all hover:-translate-y-1 hover:shadow-lg`}>
                                <div className="mt-1">{styles.icon}</div>
                                <p className="text-sm font-medium text-neutral-200 leading-relaxed">{rec.text}</p>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
};
export default RecommendationsPanel;
