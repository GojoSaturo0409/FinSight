import { useState, useEffect } from 'react';
import { apiFetch } from '../api';
import { useCurrency } from './CurrencyContext';

interface BudgetItem {
    category: string;
    limit: number;
    spent: number;
    ratio: number;
    status: string;
}

const BudgetPanel = () => {
    const { format } = useCurrency();
    const [budgets, setBudgets] = useState<BudgetItem[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchBudgets = async () => {
        try {
            const data = await apiFetch('/budget/summary');
            setBudgets(data.summary);
        } catch {
            setBudgets([]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchBudgets();
    }, []);

    const getColor = (status: string, ratio: number) => {
        if (status === 'critical') return 'bg-rose-500';
        if (status === 'exceeded') return 'bg-rose-400';
        if (status === 'warning') return 'bg-amber-400';
        if (ratio > 60) return 'bg-indigo-400';
        return 'bg-emerald-400';
    };

    const getTextColor = (status: string) => {
        if (status === 'critical' || status === 'exceeded') return 'text-rose-400';
        if (status === 'warning') return 'text-amber-400';
        return 'text-emerald-400';
    };

    const handleSliderChange = async (category: string, newLimit: number) => {
        setBudgets((prev) =>
            prev.map((b) =>
                b.category === category
                    ? { ...b, limit: newLimit, ratio: (b.spent / newLimit) * 100 }
                    : b
            )
        );

        try {
            await apiFetch('/budget/limits', {
                method: 'POST',
                body: JSON.stringify({ category, limit_amount: newLimit }),
            });
        } catch {
            // ignore
        }
    };

    return (
        <div className="bg-neutral-900/50 backdrop-blur-xl border border-white/5 rounded-2xl p-6">
            <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold">Budgets</h3>
                <span className="text-xs bg-indigo-500/20 text-indigo-300 px-2 py-1 rounded-md border border-indigo-500/30">Active</span>
            </div>

            {loading ? (
                <div className="flex justify-center py-6">
                    <div className="w-6 h-6 border-2 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin" />
                </div>
            ) : (
                <div className="space-y-6">
                    {budgets.map((budget) => (
                        <div key={budget.category}>
                            <div className="flex justify-between text-sm mb-2">
                                <span className="font-medium text-neutral-300">{budget.category}</span>
                                <span className="text-neutral-400">Limit: {format(budget.limit)}</span>
                            </div>
                            <input
                                type="range"
                                min="5"
                                max="3000"
                                step="5"
                                value={budget.limit}
                                onChange={(e) => handleSliderChange(budget.category, Number(e.target.value))}
                                className="w-full h-1 bg-neutral-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
                            />
                            <div className="flex justify-between text-xs text-neutral-500 mt-1.5">
                                <span>Spent: {format(budget.spent)}</span>
                                <span className={getTextColor(budget.status)}>
                                    {budget.ratio.toFixed(0)}% Used
                                </span>
                            </div>
                            <div className="w-full bg-neutral-800 rounded-full h-1 mt-1 border border-white/[0.02]">
                                <div
                                    className={`h-1 rounded-full transition-all duration-500 ${getColor(budget.status, budget.ratio)}`}
                                    style={{ width: `${Math.min(budget.ratio, 100)}%` }}
                                />
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};
export default BudgetPanel;
