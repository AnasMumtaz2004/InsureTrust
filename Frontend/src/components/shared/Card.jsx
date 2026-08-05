const Card = ({ children, className = '', ...props }) => {
  return (
    <div
      className={`bg-white border border-border rounded-lg ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

export default Card;
