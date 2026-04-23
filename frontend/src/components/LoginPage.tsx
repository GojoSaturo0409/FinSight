import { useState } from 'react';
import { useAuth } from './AuthContext';
import { Lock, Mail, ArrowRight } from 'lucide-react';

const LoginPage = ({ onSwitchToRegister }: { onSwitchToRegister: () => void }) => {
    const [email, setEmail] = useState('demo@finsight.app');
    const [password, setPassword] = useState('demo123');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        const { ok, error: errMsg } = await login(email, password);
        setLoading(false);
        if (!ok) setError(errMsg || 'Failed to login');
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-neutral-950 px-4">
            <div className="max-w-md w-full bg-neutral-900/50 backdrop-blur-xl border border-white/5 p-8 rounded-2xl shadow-2xl">
                <div className="text-center mb-8">
                    <div className="w-16 h-16 bg-indigo-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
                        <span className="font-bold text-3xl text-white">F</span>
                    </div>
                    <h2 className="text-3xl font-bold text-white">Welcome back</h2>
                    <p className="text-neutral-400 mt-2">Sign in to your FinSight account</p>
                </div>

                {error && <div className="bg-rose-500/10 border border-rose-500/20 text-rose-400 px-4 py-3 rounded-lg mb-6 text-sm flex justify-center">{error}</div>}

                <form onSubmit={handleSubmit} className="space-y-5">
                    <div>
                        <div className="relative">
                            <Mail className="absolute left-3 top-3.5 text-neutral-500" size={18} />
                            <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email Address" className="w-full bg-neutral-800/50 border border-white/5 rounded-xl py-3 pl-10 pr-4 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all" />
                        </div>
                    </div>
                    <div>
                        <div className="relative">
                            <Lock className="absolute left-3 top-3.5 text-neutral-500" size={18} />
                            <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" className="w-full bg-neutral-800/50 border border-white/5 rounded-xl py-3 pl-10 pr-4 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all" />
                        </div>
                    </div>
                    <button type="submit" disabled={loading} className="w-full bg-indigo-500 hover:bg-indigo-400 text-white font-bold py-3 px-4 rounded-xl transition-all disabled:opacity-50 flex items-center justify-center gap-2">
                        {loading ? 'Signing in...' : 'Sign In'}
                        <ArrowRight size={18} />
                    </button>
                    <div className="text-center mt-6 text-sm text-neutral-400">
                        Don't have an account? <button type="button" onClick={onSwitchToRegister} className="text-indigo-400 font-bold hover:underline">Register here</button>
                    </div>
                </form>
            </div>
        </div>
    );
};
export default LoginPage;
