import { useState } from 'react';
import { useAuth } from './AuthContext';
import { Lock, Mail, ArrowRight } from 'lucide-react';

const RegisterPage = ({ onSwitchToLogin }: { onSwitchToLogin: () => void }) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirm, setConfirm] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { register } = useAuth();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        if (password !== confirm) {
            setError('Passwords do not match');
            return;
        }
        setLoading(true);
        const { ok, error: errMsg } = await register(email, password);
        setLoading(false);
        if (!ok) setError(errMsg || 'Failed to register');
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-neutral-950 px-4">
            <div className="max-w-md w-full bg-neutral-900/50 backdrop-blur-xl border border-white/5 p-8 rounded-2xl shadow-2xl">
                <div className="text-center mb-8">
                    <div className="w-16 h-16 bg-gradient-to-tr from-indigo-500 to-purple-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
                        <span className="font-bold text-3xl text-white">F</span>
                    </div>
                    <h2 className="text-3xl font-bold text-white">Create Account</h2>
                    <p className="text-neutral-400 mt-2">Start managing your finances today</p>
                </div>

                {error && <div className="bg-rose-500/10 border border-rose-500/20 text-rose-400 px-4 py-3 rounded-lg mb-6 text-sm text-center">{error}</div>}

                <form onSubmit={handleSubmit} className="space-y-5">
                    <div>
                        <div className="relative">
                            <Mail className="absolute left-3 top-3.5 text-neutral-500" size={18} />
                            <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email Address" autoComplete="username" className="w-full bg-neutral-800/50 border border-white/5 rounded-xl py-3 pl-10 pr-4 text-white focus:outline-none focus:ring-2 focus:ring-purple-500/50 transition-all" />
                        </div>
                    </div>
                    <div>
                        <div className="relative">
                            <Lock className="absolute left-3 top-3.5 text-neutral-500" size={18} />
                            <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" autoComplete="new-password" className="w-full bg-neutral-800/50 border border-white/5 rounded-xl py-3 pl-10 pr-4 text-white focus:outline-none focus:ring-2 focus:ring-purple-500/50 transition-all" />
                        </div>
                    </div>
                    <div>
                        <div className="relative">
                            <Lock className="absolute left-3 top-3.5 text-neutral-500" size={18} />
                            <input type="password" required value={confirm} onChange={(e) => setConfirm(e.target.value)} placeholder="Confirm Password" autoComplete="new-password" className="w-full bg-neutral-800/50 border border-white/5 rounded-xl py-3 pl-10 pr-4 text-white focus:outline-none focus:ring-2 focus:ring-purple-500/50 transition-all" />
                        </div>
                    </div>
                    <button type="submit" disabled={loading} className="w-full bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-400 hover:to-purple-400 text-white font-bold py-3 px-4 rounded-xl transition-all disabled:opacity-50 flex items-center justify-center gap-2">
                        {loading ? 'Creating...' : 'Create Account'}
                        <ArrowRight size={18} />
                    </button>
                    <div className="text-center mt-6 text-sm text-neutral-400">
                        Already have an account? <button type="button" onClick={onSwitchToLogin} className="text-purple-400 font-bold hover:underline">Log in</button>
                    </div>
                </form>
            </div>
        </div>
    );
};
export default RegisterPage;
