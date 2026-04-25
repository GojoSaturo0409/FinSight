import { useState } from 'react';
import { apiFetch } from '../api';
import { ArrowRightLeft, DollarSign } from 'lucide-react';

const CURRENCIES = [
    { code: 'USD', name: 'US Dollar', symbol: '$' },
    { code: 'EUR', name: 'Euro', symbol: '€' },
    { code: 'GBP', name: 'British Pound', symbol: '£' },
    { code: 'JPY', name: 'Japanese Yen', symbol: '¥' },
    { code: 'INR', name: 'Indian Rupee', symbol: '₹' },
    { code: 'AUD', name: 'Australian Dollar', symbol: 'A$' },
    { code: 'CAD', name: 'Canadian Dollar', symbol: 'C$' },
    { code: 'CHF', name: 'Swiss Franc', symbol: 'Fr' },
    { code: 'CNY', name: 'Chinese Yuan', symbol: '¥' },
    { code: 'BRL', name: 'Brazilian Real', symbol: 'R$' },
];

interface ConversionResult {
    original_amount: number;
    converted_amount: number;
    rate: number;
    base_currency: string;
    target_currency: string;
}

const CurrencyConverter = () => {
    const [amount, setAmount] = useState('100');
    const [fromCurrency, setFromCurrency] = useState('USD');
    const [toCurrency, setToCurrency] = useState('EUR');
    const [result, setResult] = useState<ConversionResult | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleConvert = async () => {
        setLoading(true);
        setError('');
        try {
            const data = await apiFetch('/currency/convert', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    amount: parseFloat(amount),
                    base_currency: fromCurrency,
                    target_currency: toCurrency,
                }),
            });
            setResult(data);
        } catch (e: any) {
            setError('Conversion failed');
        } finally {
            setLoading(false);
        }
    };

    const handleSwap = () => {
        setFromCurrency(toCurrency);
        setToCurrency(fromCurrency);
        setResult(null);
    };

    const getCurrencySymbol = (code: string) => CURRENCIES.find(c => c.code === code)?.symbol || code;

    return (
        <div className="bg-neutral-900/50 backdrop-blur-xl border border-white/5 rounded-2xl p-6">
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                <DollarSign size={18} className="text-emerald-400" />
                Currency Exchange
            </h3>

            <div className="space-y-3">
                {/* Amount */}
                <div>
                    <label className="text-xs text-neutral-400 mb-1 block">Amount</label>
                    <input
                        type="number"
                        value={amount}
                        onChange={(e) => { setAmount(e.target.value); setResult(null); }}
                        className="w-full px-4 py-2.5 bg-neutral-800/50 border border-white/10 rounded-xl text-sm focus:outline-none focus:border-indigo-500/50"
                        placeholder="Enter amount..."
                    />
                </div>

                {/* From / Swap / To */}
                <div className="flex items-end gap-2">
                    <div className="flex-1">
                        <label className="text-xs text-neutral-400 mb-1 block">From</label>
                        <select
                            value={fromCurrency}
                            onChange={(e) => { setFromCurrency(e.target.value); setResult(null); }}
                            className="w-full px-3 py-2.5 bg-neutral-800/50 border border-white/10 rounded-xl text-sm focus:outline-none appearance-none cursor-pointer"
                        >
                            {CURRENCIES.map(c => <option key={c.code} value={c.code}>{c.code} — {c.name}</option>)}
                        </select>
                    </div>
                    <button onClick={handleSwap} className="p-2.5 bg-neutral-800 rounded-xl hover:bg-neutral-700 transition-colors border border-white/10" title="Swap">
                        <ArrowRightLeft size={16} className="text-indigo-400" />
                    </button>
                    <div className="flex-1">
                        <label className="text-xs text-neutral-400 mb-1 block">To</label>
                        <select
                            value={toCurrency}
                            onChange={(e) => { setToCurrency(e.target.value); setResult(null); }}
                            className="w-full px-3 py-2.5 bg-neutral-800/50 border border-white/10 rounded-xl text-sm focus:outline-none appearance-none cursor-pointer"
                        >
                            {CURRENCIES.map(c => <option key={c.code} value={c.code}>{c.code} — {c.name}</option>)}
                        </select>
                    </div>
                </div>

                {/* Convert Button */}
                <button
                    onClick={handleConvert}
                    disabled={loading || !amount}
                    className="w-full py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 rounded-xl text-sm font-medium transition-all disabled:opacity-50"
                >
                    {loading ? 'Converting...' : 'Convert'}
                </button>

                {/* Result */}
                {result && (
                    <div className="p-4 bg-neutral-800/60 rounded-xl border border-white/5 text-center">
                        <div className="text-2xl font-bold text-white">
                            {getCurrencySymbol(result.target_currency)}{result.converted_amount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                        </div>
                        <div className="text-xs text-neutral-400 mt-1">
                            {getCurrencySymbol(result.base_currency)}{result.original_amount.toLocaleString()} {result.base_currency} → {result.target_currency}
                        </div>
                        <div className="text-xs text-indigo-400 mt-1">
                            Rate: 1 {result.base_currency} = {result.rate.toFixed(4)} {result.target_currency}
                        </div>
                    </div>
                )}

                {error && <div className="text-xs text-rose-400 text-center">{error}</div>}
            </div>
        </div>
    );
};
export default CurrencyConverter;
