const Tabs = ({ tabs, activeKey, onChange, className = '' }) => {
  return (
    <div className={`flex border-b border-border ${className}`}>
      {tabs.map((tab) => (
        <button
          key={tab.key}
          onClick={() => onChange(tab.key)}
          className={`px-4 py-2.5 text-sm font-medium transition-tab border-b-2 cursor-pointer ${
            activeKey === tab.key
              ? 'text-accent border-accent'
              : 'text-secondary border-transparent hover:text-primary hover:border-border'
          }`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
};

export default Tabs;
