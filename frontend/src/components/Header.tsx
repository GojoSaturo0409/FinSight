
interface HeaderProps {
    activeTab: string;
    onTabChange: (tab: string) => void;
}

const tabs = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'analytics', label: 'Analytics' },
    { id: 'investments', label: 'Investments' },
    { id: 'reports', label: 'Reports' },
];

const Header = ({ activeTab, onTabChange }: HeaderProps) => (
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
                        className={`px-4 py-2 rounded-lg transition-all duration-200 ${
                            activeTab === tab.id
                                ? 'text-white bg-white/5'
                                : 'text-neutral-400 hover:text-white hover:bg-white/[0.03]'
                        }`}
                    >
                        {tab.label}
                    </button>
                ))}
            </nav>
            <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 border-2 border-neutral-950 shadow-inner"></div>
        </div>
    </header>
);

export default Header;
