import { useState } from 'react';
import { Plus, CheckCircle2, Loader2 } from 'lucide-react';
import { apiFetch } from '../api';

const ManualEntryForm = ({ onTransactionAdded }: { onTransactionAdded: () => void }) => {
    const [open, setOpen] = useState(false);
    const [type, setType] = useState<'expense' | 'income'>('expense');
    const [amount, setAmount] = useState('');
    const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
    const [category, setCategory] = useState('Food');
    const [merchant, setMerchant] = useState('');
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            await apiFetch('/ingestion/manual', {
                method: 'POST',
                body: JSON.stringify({
                    amount: parseFloat(amount),
                    date,
                    category: type === 'income' ? 'Income' : category,
                    merchant,
                    currency: 'USD'
                })
            });
            await apiFetch('/budget/evaluate-auto', { method: 'POST' });
            setSuccess(true);
            setTimeout(() => {
                setSuccess(false);
                setOpen(false);
                onTransactionAdded();
                setAmount('');
                setMerchant('');
            }, 1000);
        } catch {
            // ignore for now
        } finally {
            setLoading(false);
        }
    };

    if (!open) {
        return (
            <button onClick={() => setOpen(true)} className="w-full bg-neutral-900/50 border border-white/5 rounded-2xl p-6 flex flex-col items-center justify-center gap-3 hover:bg-neutral-800/50 transition-colors group">
                <div className="w-12 h-12 rounded-full bg-indigo-500/10 flex items-center justify-center group-hover:bg-indigo-500/20 transition-colors">
                    <Plus className="text-indigo-400" />
                </div>
                <span className="font-medium text-neutral-300">Add Manual Transaction</span>
            </button>
        );
    }

    return (
        <div className="bg-neutral-900/50 border border-white/5 rounded-2xl p-6">
            <h3 className="text-lg font-bold mb-4">New Transaction</h3>
            
            <div className="flex rounded-xl bg-neutral-800/50 p-1 mb-4 border border-white/5">
                <button 
                    onClick={() => setType('expense')}
                    className={`flex-1 py-1.5 rounded-lg text-sm font-medium transition-colors ${type === 'expense' ? 'bg-neutral-700 text-white shadow-sm' : 'text-neutral-400 hover:text-neutral-200'}`}
                >
                    Deduct (Expense)
                </button>
                <button 
                    onClick={() => setType('income')}
                    className={`flex-1 py-1.5 rounded-lg text-sm font-medium transition-colors ${type === 'income' ? 'bg-emerald-600 outline-none text-white shadow-sm' : 'text-neutral-400 hover:text-neutral-200'}`}
                >
                    Add (Income)
                </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
                <input type="number" step="0.01" required value={amount} onChange={e => setAmount(e.target.value)} placeholder="Amount (e.g. 50.00)" className="w-full bg-neutral-800/50 border border-white/5 rounded-xl py-2 px-3 text-white focus:ring-1 focus:ring-indigo-500/30" />
                <input type="date" required value={date} onChange={e => setDate(e.target.value)} className="w-full bg-neutral-800/50 border border-white/5 rounded-xl py-2 px-3 text-white focus:ring-1 focus:ring-indigo-500/30" />
                <input type="text" required value={merchant} onChange={e => setMerchant(e.target.value)} placeholder={type === 'income' ? 'Source (e.g. Company, Friend)' : 'Merchant'} className="w-full bg-neutral-800/50 border border-white/5 rounded-xl py-2 px-3 text-white focus:ring-1 focus:ring-indigo-500/30" />
                
                {type === 'expense' && (
                    <select value={category} onChange={e => setCategory(e.target.value)} className="w-full bg-neutral-800/50 border border-white/5 rounded-xl py-2 px-3 text-white focus:ring-1 focus:ring-indigo-500/30">
                        <option value="Food">Food</option>
                        <option value="Housing">Housing</option>
                        <option value="Transport">Transport</option>
                        <option value="Shopping">Shopping</option>
                        <option value="Entertainment">Entertainment</option>
                        <option value="Utilities">Utilities</option>
                    </select>
                )}

                <div className="flex gap-2 pt-2">
                    <button type="button" onClick={() => setOpen(false)} className="flex-1 py-2 rounded-xl border border-white/5 text-neutral-400 hover:text-white">Cancel</button>
                    <button type="submit" disabled={loading} className={`flex-1 py-2 rounded-xl text-white font-bold flex items-center justify-center gap-2 ${type === 'income' ? 'bg-emerald-500' : 'bg-indigo-500'}`}>
                        {loading ? <Loader2 size={16} className="animate-spin" /> : success ? <CheckCircle2 size={16} /> : 'Save'}
                    </button>
                </div>
            </form>
        </div>
    );
};
export default ManualEntryForm;
