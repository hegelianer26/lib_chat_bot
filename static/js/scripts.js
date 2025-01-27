function toggleSubtree(btn) {
    const li = btn.closest('li');
    if (!li) return;
    const subCat = li.querySelector('.subcategory');
    if (!subCat) return;

    subCat.classList.toggle('hidden');
    btn.textContent = subCat.classList.contains('hidden') ? '[+]' : '[-]';
}

function showFullImage(src) {
    const modal = document.getElementById('imageModal');
    const modalImg = document.getElementById('modalImage');
    modal.style.display = "block";
    modalImg.src = src;
}

function closeModal() {
    document.getElementById('imageModal').style.display = "none";
}

window.onclick = function(event) {
    const modal = document.getElementById('imageModal');
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

// Инициализация TinyMCE для добавления нового ответа
tinymce.init({
    selector: 'textarea[name="answer_text"]',
    plugins: 'emoticons',
    toolbar: 'undo redo | emoticons',
    menubar: false,
    setup: function(editor) {
        editor.on('change', function() {
            editor.save(); // Save content to textarea
        });
    }
});

// Функция для инициализации TinyMCE для редактирования ответа
function initEditAnswerTinyMCE(answerId) {
    tinymce.init({
        selector: `#edit-answer-${answerId}`,
        plugins: 'emoticons',
        toolbar: 'undo redo | emoticons',
        menubar: false,
        setup: function(editor) {
            editor.on('change', function() {
                document.querySelector(`#hidden-edit-${answerId}`).value = editor.getContent();
            });
        }
    });
}

// Функция для отображения формы редактирования
function showEditForm(answerId) {
    const viewElement = document.querySelector(`#view-answer-${answerId}`);
    const editElement = document.querySelector(`#edit-form-${answerId}`);
    viewElement.style.display = 'none';
    editElement.style.display = 'block';
    initEditAnswerTinyMCE(answerId);
}

// Функция для скрытия формы редактирования
function hideEditForm(answerId) {
    const viewElement = document.querySelector(`#view-answer-${answerId}`);
    const editElement = document.querySelector(`#edit-form-${answerId}`);
    viewElement.style.display = 'block';
    editElement.style.display = 'none';
    tinymce.remove(`#edit-answer-${answerId}`);
}

// Обработчик отправки формы редактирования
document.querySelectorAll('.edit-answer-form').forEach(form => {
    form.addEventListener('submit', function(e) {
        const answerId = this.querySelector('[name="ans_id"]').value;
        const content = tinymce.get(`edit-answer-${answerId}`).getContent();
        this.querySelector('[name="new_text"]').value = content;
    });
});


    // Функция для сворачивания всех категорий и ответов
    function collapseAll() {
        document.querySelectorAll('.subcategory').forEach(subCat => {
            subCat.classList.add('hidden');
        });
        document.querySelectorAll('.toggle-btn').forEach(btn => {
            btn.textContent = '[+]';
        });
    }

    // Функция для разворачивания всех категорий и ответов
    function expandAll() {
        document.querySelectorAll('.subcategory').forEach(subCat => {
            subCat.classList.remove('hidden');
        });
        document.querySelectorAll('.toggle-btn').forEach(btn => {
            btn.textContent = '[-]';
        });
    }

    $(document).ready(function() {
    $('.category-select').select2({
        placeholder: "Выберите категорию",
        allowClear: true,
        width: '100%', // Это можно настроить в соответствии с вашими потребностями
    });
    $('.category-select').select2('destroy').select2();

});


document.addEventListener('DOMContentLoaded', function() {
    // Функция для отображения flash-сообщений
    function showFlashMessage(message, category) {
        const flashMessagesContainer = document.querySelector('.flash-messages-container');
        if (!flashMessagesContainer) {
            console.error('Flash messages container not found');
            return;
        }

        const alert = document.createElement('div');
        alert.className = `alert alert-${category} animate__animated animate__fadeIn`;
        alert.innerHTML = `
            <div class="alert-content">
                <span class="alert-icon">${category === 'success' ? '✅' : '❌'}</span>
                <span class="alert-message">${message}</span>
            </div>
            <button class="alert-close" onclick="this.parentElement.remove();">&times;</button>
        `;
        flashMessagesContainer.appendChild(alert);

        // Автоматически удалить сообщение через 5 секунд
        setTimeout(() => {
            alert.classList.remove('animate__fadeIn');
            alert.classList.add('animate__fadeOut');
            setTimeout(() => {
                alert.remove();
            }, 1000);
        }, 5000);
    }

    // Обработчик отправки формы добавления категории
    const addCategoryForm = document.getElementById('add-category-form');
    if (addCategoryForm) {
        addCategoryForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            fetch('/dialogs/add_category', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    showFlashMessage(data.message, 'success');
                    // Обновить список категорий на странице
                    updateCategoryList(data.category);
                    // Очистить форму
                    this.reset();
                } else {
                    showFlashMessage(data.message, 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showFlashMessage('Произошла ошибка при добавлении категории', 'error');
            });
        });
    }

    // Функция для обновления списка категорий
    function updateCategoryList(newCategory) {
        const categoryList = document.getElementById('category-list');
        if (categoryList) {
            const newItem = document.createElement('li');
            newItem.setAttribute('data-category-id', newCategory.id);
            newItem.innerHTML = `
                ${newCategory.name}
                <button onclick="deleteCategory(${newCategory.id})">Удалить</button>
            `;
            categoryList.appendChild(newItem);
        }
    }
});