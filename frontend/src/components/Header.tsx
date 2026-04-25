import { useAuth } from './AuthContext';
import { useCurrency, SUPPORTED_CURRENCIES } from './CurrencyContext';
import { LogOut, Menu, X } from 'lucide-react';
import { useState } from 'react';

interface HeaderProps {
    activeTab: string;
    onTabChange: (tab: string) => void;
}

const tabs = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'analytics', label: 'Analytics & Insights' },
    { id: 'investments', label: 'Investments' },
    { id: 'reports', label: 'Reports' },
];

const Header = ({ activeTab, onTabChange }: HeaderProps) => {
    const { user, logout } = useAuth();
    const { baseCurrency, setBaseCurrency } = useCurrency();
    const [mobileOpen, setMobileOpen] = useState(false);

    return (
        <header className="border-b border-white/5 bg-neutral-950/80 backdrop-blur-md sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-indigo-500 rounded-xl flex items-center justify-center">
                        <span className="font-bold text-xl text-white">F</span>
                    </div>
                    <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-white/60">
                        FinSight
                    </h1>
                </div>

                <nav className="hidden md:flex items-center gap-1 text-sm font-medium">
                    {tabs.map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => onTabChange(tab.id)}
                            className={`px-4 py-2 rounded-lg transition-all duration-200 ${activeTab === tab.id
                                ? 'text-white bg-white/5'
                                : 'text-neutral-400 hover:text-white hover:bg-white/[0.03]'
                                }`}
                        >
                            {tab.label}
                        </button>
                    ))}
                </nav>

                <div className="flex items-center gap-3">
                    {user && (
                        <span className="hidden md:inline text-xs text-neutral-500">{user.email}</span>
                    )}
                    
                    <select
                        value={baseCurrency}
                        onChange={(e) => setBaseCurrency(e.target.value)}
                        className="bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-xs font-medium text-white px-2.5 py-1.5 focus:outline-none focus:border-indigo-500/50 transition-colors cursor-pointer appearance-none outline-none"
                    >
                        {SUPPORTED_CURRENCIES.map(c => (
                            <option key={c.code} value={c.code} className="bg-neutral-900 text-white">
                                {c.code} ({c.symbol})
                            </option>
                        ))}
                    </select>
                    <button
                        onClick={logout}
                        className="hidden md:flex items-center gap-1.5 text-xs text-neutral-500 hover:text-rose-400 transition-colors px-3 py-2 rounded-lg hover:bg-rose-500/5"
                        title="Sign Out"
                    >
                        <LogOut size={14} />
                        <span>Sign Out</span>
                    </button>

                    <button
                        onClick={() => setMobileOpen(!mobileOpen)}
                        className="md:hidden text-neutral-400 hover:text-white"
                    >
                        {mobileOpen ? <X size={24} /> : <Menu size={24} />}
                    </button>
                </div>
            </div>

            {mobileOpen && (
                <div className="md:hidden border-t border-white/5 bg-neutral-950 px-4 py-3 space-y-1">
                    {tabs.map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => { onTabChange(tab.id); setMobileOpen(false); }}
                            className={`w-full text-left px-4 py-2.5 rounded-lg text-sm ${activeTab === tab.id
                                ? 'text-white bg-white/5'
                                : 'text-neutral-400'
                                }`}
                        >
                            {tab.label}
                        </button>
                    ))}
                    <button
                        onClick={logout}
                        className="w-full text-left px-4 py-2.5 rounded-lg text-sm text-rose-400 hover:bg-rose-500/5"
                    >
                        <LogOut size={14} className="inline mr-2" />
                        Sign Out
                    </button>
                </div>
            )}
        </header>
    );
};
export default Header;
