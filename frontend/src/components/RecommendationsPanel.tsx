import { useState, useEffect } from 'react';
import { AlertTriangle, Lightbulb, CheckCircle, Zap } from 'lucide-react';

interface Recommendation {
    text: string;
    type: 'warning' | 'tip' | 'success';
}

const RecommendationsPanel = () => {
    const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        generateRecommendations();
    }, []);

    const generateRecommendations = async () => {
        setLoading(true);

        // Simulate calling POST /recommendations/generate
        // In production, this would be a real fetch call
        const mockContext = {
            monthly_income: 5000,
            monthly_spend: 1716.49,
            savings_target: 1500,
            categories: {
                Housing: 1500,
                Food: 300,
                Transport: 150,
                Subscriptions: 50,
            },
            recurring_merchants: ['Netflix', 'Spotify', 'iCloud'],
        };

        try {
            // Try real API first
            const response = await fetch('http://localhost:8000/recommendations/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(mockContext),
            });

            if (response.ok) {
                const data = await response.json();
                const recs = data.recommendations.map((r: string) => ({
                    text: r,
                    type: classifyRecommendation(r),
                }));
                setRecommendations(recs);
            } else {
                throw new Error('API unavailable');
            }
        } catch {
            // Fallback to mock recommendations
            setRecommendations([
                { text: "Category Alert: 'Housing' is 30.0% of your income ($1500/$5000). The recommended limit per category is 30%.", type: 'warning' },
                { text: "Recurring Charges Detected: Netflix, Spotify, iCloud. Check if all of these are still needed.", type: 'tip' },
                { text: "Great job! You hit your monthly savings target of $1500 with $3284 saved (218.9%). You have an extra $1784 this month.", type: 'success' },
                { text: "Investment Opportunity: You have a surplus of $3284. Consider investing in low-risk index funds. Market snapshot: SPY: $523.40 ↑ | BND: $72.85 ↑ | VTI: $261.20 ↑", type: 'tip' },
            ]);
        } finally {
            setLoading(false);
        }
    };

    const classifyRecommendation = (text: string): 'warning' | 'tip' | 'success' => {
        if (text.includes('Warning') || text.includes('Alert') || text.includes('Audit')) return 'warning';
        if (text.includes('Great job') || text.includes('hit your')) return 'success';
        return 'tip';
    };

    const getIcon = (type: string) => {
        switch (type) {
            case 'warning': return <AlertTriangle size={18} />;
            case 'success': return <CheckCircle size={18} />;
            default: return <Lightbulb size={18} />;
        }
    };

    const getStyles = (type: string) => {
        switch (type) {
            case 'warning':
                return 'bg-rose-500/10 border-rose-500/20 text-rose-300';
            case 'success':
                return 'bg-emerald-500/10 border-emerald-500/20 text-emerald-300';
            default:
                return 'bg-indigo-500/10 border-indigo-500/20 text-indigo-300';
        }
    };

    return (
        <div className="bg-neutral-900/50 backdrop-blur-xl border border-white/5 rounded-2xl p-6">
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2">
                    <Zap size={20} className="text-amber-400" />
                    <h3 className="text-xl font-bold">Recommendations</h3>
                </div>
                <button
                    onClick={generateRecommendations}
                    className="text-xs bg-neutral-800 text-neutral-300 px-3 py-1.5 rounded-lg border border-white/5 hover:border-white/10 hover:bg-neutral-700 transition-all"
                >
                    Refresh
                </button>
            </div>

            {loading ? (
                <div className="flex items-center justify-center py-8">
                    <div className="w-6 h-6 border-2 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin" />
                </div>
            ) : (
                <div className="space-y-3">
                    {recommendations.map((rec, idx) => (
                        <div
                            key={idx}
                            className={`flex items-start gap-3 p-4 rounded-xl border transition-all duration-300 ${getStyles(rec.type)}`}
                            style={{
                                animation: `fadeSlideIn 0.4s ease-out ${idx * 0.1}s both`,
                            }}
                        >
                            <div className="mt-0.5 shrink-0">{getIcon(rec.type)}</div>
                            <p className="text-sm leading-relaxed">{rec.text}</p>
                        </div>
                    ))}
                </div>
            )}

            <style>{`
                @keyframes fadeSlideIn {
                    from {
                        opacity: 0;
                        transform: translateY(10px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
            `}</style>
        </div>
    );
};

export default RecommendationsPanel;
