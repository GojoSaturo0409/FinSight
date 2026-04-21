
const TransactionTable = ({ transactions }: { transactions: any[] }) => {
    return (
        <div className="bg-neutral-900/50 backdrop-blur-xl border border-white/5 rounded-2xl p-6">
            <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold">Recent Transactions</h3>
                <button className="text-indigo-400 text-sm font-medium hover:text-indigo-300 transition-colors">View All</button>
            </div>
            <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="text-neutral-500 text-xs uppercase tracking-wider border-b border-white/5">
                            <th className="pb-3 font-medium">Merchant</th>
                            <th className="pb-3 font-medium">Category</th>
                            <th className="pb-3 font-medium">Date</th>
                            <th className="pb-3 font-medium text-right">Amount</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        {transactions.map((tx) => (
                            <tr key={tx.id} className="group hover:bg-white/[0.02] transition-colors">
                                <td className="py-4 text-sm font-medium flex hidden sm:block truncate mt-1">
                                    {tx.merchant}
                                </td>
                                <td className="py-2 sm:py-4">
                                    <span className="px-3 py-1 bg-neutral-800 text-neutral-300 text-xs rounded-full border border-white/5 group-hover:border-white/10 transition-colors">
                                        {tx.category}
                                    </span>
                                </td>
                                <td className="py-4 text-sm text-neutral-400">{tx.date}</td>
                                <td className="py-4 text-sm font-bold text-right text-emerald-400">
                                    -${tx.amount.toFixed(2)}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default TransactionTable;
