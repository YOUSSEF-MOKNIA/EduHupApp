import React from 'react';

const ConfirmationModal = ({ open, onClose, onConfirm, title, confirmationText }) => {
  if (!open) return null; // If the modal is not open, don't render it

  return (
    // Modal overlay with blurred background
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm z-50">
      {/* Modal content */}
      <div className="bg-white p-6 rounded-lg shadow-lg w-96">
        {/* Modal Title */}
        <h2 className="text-2xl font-semibold mb-4 text-gray">
          {title || 'Confirmation'} {/* Default title if not provided */}
        </h2>
        
        {/* Confirmation text */}
        <p className="text-gray mb-6">
          {confirmationText || 'Are you sure you want to proceed?'} {/* Default text if not provided */}
        </p>

        {/* Modal action buttons */}
        <div className="flex justify-end space-x-4">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-light-blue rounded hover:bg-blue hover:text-white"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm} // Call the onConfirm function from TopBar when clicked
            className="px-4 py-2 bg-light-orange text-black rounded hover:bg-error hover:text-white"
          >
            Confirm
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmationModal;
