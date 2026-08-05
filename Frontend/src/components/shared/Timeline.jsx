const Timeline = ({ items }) => {
  return (
    <div className="relative">
      {items.map((item, index) => (
        <div key={index} className="flex gap-4 pb-6 last:pb-0">
          {/* Line + Dot */}
          <div className="flex flex-col items-center">
            <div className={`w-3 h-3 rounded-full border-2 ${
              item.active ? 'border-accent bg-accent' : 'border-border bg-white'
            }`} />
            {index < items.length - 1 && (
              <div className="w-0.5 flex-1 bg-border mt-1" />
            )}
          </div>
          {/* Content */}
          <div className="flex-1 -mt-1">
            <p className="text-sm font-medium text-primary">{item.title}</p>
            {item.description && (
              <p className="text-xs text-secondary mt-0.5">{item.description}</p>
            )}
            {item.timestamp && (
              <p className="text-xs text-secondary mt-1">{item.timestamp}</p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default Timeline;
