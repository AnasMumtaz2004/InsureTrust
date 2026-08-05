const IconButton = ({ icon: Icon, size = 20, active = false, badge, className = '', ...props }) => {
  return (
    <button
      className={`relative p-2 rounded-full transition-colors duration-150 cursor-pointer ${
        active
          ? 'bg-accent/10 text-accent'
          : 'text-secondary hover:bg-background hover:text-primary'
      } ${className}`}
      {...props}
    >
      <Icon size={size} />
      {badge && (
        <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-accent text-white text-[10px] font-bold rounded-full flex items-center justify-center">
          {badge}
        </span>
      )}
    </button>
  );
};

export default IconButton;
