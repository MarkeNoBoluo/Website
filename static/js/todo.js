/**
 * Eisenhower Matrix Todo Drag & Drop Functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize drag and drop
    initDragAndDrop();

    // Initialize priority sorting
    initPrioritySorting();
});

/**
 * Initialize drag and drop for moving tasks between quadrants
 */
function initDragAndDrop() {
    const taskCards = document.querySelectorAll('.task-card');
    const quadrants = document.querySelectorAll('.quadrant .tasks-list');

    // Set up draggable task cards
    taskCards.forEach(card => {
        card.setAttribute('draggable', 'true');
        card.addEventListener('dragstart', handleDragStart);
        card.addEventListener('dragend', handleDragEnd);
    });

    // Set up drop zones (quadrants)
    quadrants.forEach(quadrant => {
        quadrant.addEventListener('dragover', handleDragOver);
        quadrant.addEventListener('dragenter', handleDragEnter);
        quadrant.addEventListener('dragleave', handleDragLeave);
        quadrant.addEventListener('drop', handleDrop);
    });
}

/**
 * Initialize drag and drop for priority sorting within quadrants
 */
function initPrioritySorting() {
    const quadrants = document.querySelectorAll('.quadrant .tasks-list');

    quadrants.forEach(quadrant => {
        // Make quadrant a sortable container
        quadrant.addEventListener('dragover', function(e) {
            e.preventDefault();
            const afterElement = getDragAfterElement(quadrant, e.clientY);
            const draggable = document.querySelector('.dragging');

            if (afterElement == null) {
                quadrant.appendChild(draggable);
            } else {
                quadrant.insertBefore(draggable, afterElement);
            }
        });

        quadrant.addEventListener('drop', function(e) {
            e.preventDefault();
            const draggable = document.querySelector('.dragging');
            if (draggable) {
                updateTaskPriority(draggable);
            }
        });
    });
}

// Drag and drop event handlers
function handleDragStart(e) {
    this.classList.add('dragging');
    e.dataTransfer.setData('text/plain', this.dataset.taskId);
    e.dataTransfer.effectAllowed = 'move';
}

function handleDragEnd(e) {
    this.classList.remove('dragging');
    // Remove visual feedback from all quadrants
    document.querySelectorAll('.quadrant .tasks-list').forEach(q => {
        q.classList.remove('drag-over');
    });
}

function handleDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
}

function handleDragEnter(e) {
    e.preventDefault();
    this.classList.add('drag-over');
}

function handleDragLeave(e) {
    this.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    this.classList.remove('drag-over');

    const taskId = e.dataTransfer.getData('text/plain');
    const taskCard = document.querySelector(`[data-task-id="${taskId}"]`);
    const newQuadrant = this.closest('.quadrant').dataset.quadrant;

    if (taskCard && newQuadrant) {
        // Move task card to new quadrant
        this.appendChild(taskCard);

        // Update quadrant on server
        updateTaskQuadrant(taskId, newQuadrant);

        // Update priority based on new position
        updateTaskPriority(taskCard);
    }
}

/**
 * Calculate new priority based on position in quadrant
 */
function updateTaskPriority(taskCard) {
    const quadrant = taskCard.closest('.tasks-list');
    const taskCards = Array.from(quadrant.querySelectorAll('.task-card'));
    const taskId = taskCard.dataset.taskId;

    // Priority is based on position: first = highest priority (1)
    const newPriority = taskCards.indexOf(taskCard) + 1;

    // Update visual priority indicator
    const priorityIndicator = taskCard.querySelector('.priority-indicator');
    if (priorityIndicator) {
        priorityIndicator.className = `priority-indicator priority-${newPriority}`;
    }

    // Update data attribute
    taskCard.dataset.priority = newPriority;

    // Update priority on server
    updateTaskPriorityOnServer(taskId, newPriority);
}

/**
 * Get element after which to insert dragged element
 */
function getDragAfterElement(container, y) {
    const draggableElements = [...container.querySelectorAll('.task-card:not(.dragging)')];

    return draggableElements.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;

        if (offset < 0 && offset > closest.offset) {
            return { offset: offset, element: child };
        } else {
            return closest;
        }
    }, { offset: Number.NEGATIVE_INFINITY }).element;
}

/**
 * Send quadrant update to server
 */
function updateTaskQuadrant(taskId, quadrant) {
    const formData = new FormData();
    formData.append('csrf_token', getCsrfToken());
    formData.append('quadrant', quadrant);

    fetch(`/todo/${taskId}/move`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            console.error('Failed to update quadrant');
            // Optionally revert visual change
        }
    })
    .catch(error => {
        console.error('Error updating quadrant:', error);
    });
}

/**
 * Send priority update to server
 */
function updateTaskPriorityOnServer(taskId, priority) {
    const formData = new FormData();
    formData.append('csrf_token', getCsrfToken());
    formData.append('priority', priority);

    fetch(`/todo/${taskId}/reorder`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            console.error('Failed to update priority');
        }
    })
    .catch(error => {
        console.error('Error updating priority:', error);
    });
}

/**
 * Get CSRF token from meta tag or form input
 */
function getCsrfToken() {
    // Check meta tag
    const metaToken = document.querySelector('meta[name="csrf-token"]');
    if (metaToken) {
        return metaToken.getAttribute('content');
    }

    // Check first form input with name csrf_token
    const formToken = document.querySelector('input[name="csrf_token"]');
    if (formToken) {
        return formToken.value;
    }

    console.warn('CSRF token not found');
    return '';
}