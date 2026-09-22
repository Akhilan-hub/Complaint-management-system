// Client-side interactions for Complaint Management System

document.addEventListener('DOMContentLoaded', function() {
    // Image Upload Live Preview
    const fileInputs = document.querySelectorAll('.form-file-input');
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const targetPreviewId = input.dataset.previewTarget;
                if (targetPreviewId) {
                    const previewElement = document.getElementById(targetPreviewId);
                    if (previewElement) {
                        const reader = new FileReader();
                        reader.onload = function(evt) {
                            previewElement.src = evt.target.result;
                            previewElement.style.display = 'block';
                        };
                        reader.readAsDataURL(file);
                    }
                }
            }
        });
    });

    // Modal Dialog Controls
    const openModalButtons = document.querySelectorAll('[data-open-modal]');
    const closeModalButtons = document.querySelectorAll('[data-close-modal]');

    openModalButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const modalId = btn.dataset.openModal;
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.classList.add('active');
            }
        });
    });

    closeModalButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const modal = btn.closest('.modal-overlay');
            if (modal) {
                modal.classList.remove('active');
            }
        });
    });

    // --- Delete Mode Controls ---
    const toggleDeleteModeBtn = document.getElementById('toggle-delete-mode-btn');
    const deleteModeControls = document.getElementById('delete-mode-controls');
    const cancelDeleteModeBtn = document.getElementById('cancel-delete-mode-btn');
    const triggerBulkDeleteModalBtn = document.getElementById('trigger-bulk-delete-modal-btn');
    const confirmDeleteSubmitBtn = document.getElementById('confirm-delete-submit-btn');

    const selectAllCheckbox = document.getElementById('select-all-complaints');
    const complaintCheckboxes = document.querySelectorAll('.complaint-checkbox');
    const deleteCols = document.querySelectorAll('.delete-col');
    const selectedCountSpan = document.getElementById('selected-count');
    const bulkDeleteForm = document.getElementById('bulk-delete-form');
    const deleteConfirmModal = document.getElementById('delete-confirm-modal');

    function updateDeleteSelectionState() {
        const checkedBoxes = document.querySelectorAll('.complaint-checkbox:checked');
        const count = checkedBoxes.length;

        if (selectedCountSpan) {
            selectedCountSpan.textContent = count;
        }

        if (triggerBulkDeleteModalBtn) {
            triggerBulkDeleteModalBtn.disabled = (count === 0);
        }

        if (selectAllCheckbox && complaintCheckboxes.length > 0) {
            selectAllCheckbox.checked = (count === complaintCheckboxes.length);
        }
    }

    if (toggleDeleteModeBtn) {
        toggleDeleteModeBtn.addEventListener('click', function(e) {
            e.preventDefault();
            toggleDeleteModeBtn.style.display = 'none';
            if (deleteModeControls) deleteModeControls.style.display = 'inline-flex';
            deleteCols.forEach(col => {
                col.style.display = 'table-cell';
            });
            updateDeleteSelectionState();
        });
    }

    if (cancelDeleteModeBtn) {
        cancelDeleteModeBtn.addEventListener('click', function(e) {
            e.preventDefault();
            if (deleteModeControls) deleteModeControls.style.display = 'none';
            if (toggleDeleteModeBtn) toggleDeleteModeBtn.style.display = 'inline-flex';
            deleteCols.forEach(col => {
                col.style.display = 'none';
            });
            // Uncheck all boxes
            if (selectAllCheckbox) selectAllCheckbox.checked = false;
            complaintCheckboxes.forEach(cb => { cb.checked = false; });
            updateDeleteSelectionState();
        });
    }

    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const isChecked = selectAllCheckbox.checked;
            complaintCheckboxes.forEach(cb => {
                cb.checked = isChecked;
            });
            updateDeleteSelectionState();
        });
    }

    complaintCheckboxes.forEach(cb => {
        cb.addEventListener('change', updateDeleteSelectionState);
    });

    if (triggerBulkDeleteModalBtn) {
        triggerBulkDeleteModalBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const checkedBoxes = document.querySelectorAll('.complaint-checkbox:checked');
            if (checkedBoxes.length > 0 && deleteConfirmModal) {
                deleteConfirmModal.classList.add('active');
            }
        });
    }

    if (confirmDeleteSubmitBtn) {
        confirmDeleteSubmitBtn.addEventListener('click', function(e) {
            e.preventDefault();
            if (bulkDeleteForm) {
                bulkDeleteForm.submit();
            }
        });
    }
});
