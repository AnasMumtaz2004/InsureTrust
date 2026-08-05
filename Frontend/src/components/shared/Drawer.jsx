import { useEffect, useCallback } from 'react';
import { X } from 'lucide-react';

const Drawer = ({ isOpen, onClose, title, children, width = 'max-w-lg' }) => {
  const handleEscape = useCallback((e) => {
    if (e.key === 'Escape') onClose();
  }, [onClose]);

  useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = '';
    };
  }, [isOpen, handleEscape]);

  return (
    <>
      {/* Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-primary/50 z-40 transition-modal"
          onClick={onClose}
        />
      )}
      {/* Drawer panel */}
      <div
        className={`fixed top-0 right-0 h-full ${width} w-full bg-white border-l border-border z-50 transition-drawer ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-border">
          <h3 className="text-lg font-semibold text-primary">{title}</h3>
          <button
            onClick={onClose}
            className="p-1 rounded-md hover:bg-background text-secondary cursor-pointer"
          >
            <X size={18} />
          </button>
        </div>
        {/* Content */}
        <div className="p-6 overflow-y-auto h-[calc(100%-65px)]">
          {children}
        </div>
      </div>
    </>
  );
};

export default Drawer;
