import { useState } from 'react';
import { useCurrency } from './CurrencyContext';

const TransactionTable = ({ transactions, onRefresh }: { transactions: any[]; onRefresh?: () => void }) => {
    const { format } = useCurrency();
    const [filter, setFilter] = useState('');

    const filtered = (transactions || []).filter((tx) => {
        if (!filter) return true;
        return (
            (tx.merchant && tx.merchant.toLowerCase().includes(filter.toLowerCase())) ||
            (tx.category && tx.category.toLowerCase().includes(filter.toLowerCase()))
        );
    });

    return (
        <div className="bg-neutral-900/50 backdrop-blur-xl border border-white/5 rounded-2xl p-6">
            <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold">Recent Transactions</h3>
                <div className="flex items-center gap-3">
                    <input
                        type="text"
                        value={filter}
                        onChange={(e) => setFilter(e.target.value)}
                        placeholder="Filter..."
                        className="bg-neutral-800/50 border border-white/5 rounded-lg py-1.5 px-3 text-xs text-white w-32 focus:outline-none focus:ring-1 focus:ring-indigo-500/30 transition-all placeholder:text-neutral-600"
                    />
                    {onRefresh && (
                        <button
                            onClick={onRefresh}
                            className="text-indigo-400 text-sm font-medium hover:text-indigo-300 transition-colors"
                        >
                            Refresh
                        </button>
                    )}
                </div>
            </div>
            <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="border-b border-white/5 text-xs text-neutral-500 uppercase tracking-wider">
                            <th className="py-3 font-medium">Merchant</th>
                            <th className="py-3 font-medium">Category</th>
                            <th className="py-3 font-medium">Date</th>
                            <th className="py-3 font-medium text-right">Amount</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        {filtered.length === 0 ? (
                            <tr>
                                <td colSpan={4} className="py-8 text-center text-neutral-500 text-sm">
                                    No transactions found
                                </td>
                            </tr>
                        ) : (
                            filtered.map((tx) => (
                                <tr key={tx.id} className="group hover:bg-white/[0.02] transition-colors">
                                    <td className="py-4 text-sm font-medium truncate max-w-[180px]">
                                        {tx.merchant}
                                    </td>
                                    <td className="py-4">
                                        <span className="px-3 py-1 bg-neutral-800 text-neutral-300 text-xs rounded-full border border-white/5 group-hover:border-white/10 transition-colors">
                                            {tx.category}
                                        </span>
                                    </td>
                                    <td className="py-4 text-sm text-neutral-400">{tx.date}</td>
                                    <td className={`py-4 text-sm font-bold text-right ${tx.category === 'Income' ? 'text-emerald-400' : 'text-rose-400'}`}>
                                        {tx.category === 'Income' ? '+' : '-'}{format(Math.abs(tx.amount))}
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
            <div className="mt-4 text-xs text-neutral-600 text-right">
                {filtered.length} transaction{filtered.length !== 1 ? 's' : ''}
            </div>
        </div>
    );
};
export default TransactionTable;
