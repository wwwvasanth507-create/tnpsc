// Admin Control Panel JS Helpers - Pure Vanilla JS
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.remove('hidden');
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.add('hidden');
}

function editSubject(id, name, code, description, orderIndex, isActive) {
    const form = document.getElementById('edit-subject-form');
    if (form) {
        form.action = `/admin/subjects/${id}/edit`;
        document.getElementById('edit-name').value = name;
        document.getElementById('edit-code').value = code;
        document.getElementById('edit-description').value = description;
        document.getElementById('edit-order').value = orderIndex;
        document.getElementById('edit-active').checked = isActive;
        openModal('edit-subject-modal');
    }
}
