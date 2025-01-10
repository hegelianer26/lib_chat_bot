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
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(function(message) {
      // Анимация появления
      message.style.opacity = '0';
      message.style.transform = 'translateY(-20px)';
      setTimeout(() => {
        message.style.opacity = '1';
        message.style.transform = 'translateY(0)';
      }, 100);
  
      // Автоматически скрывать сообщение через 5 секунд
      setTimeout(function() {
        message.style.opacity = '0';
        message.style.transform = 'translateY(-20px)';
        setTimeout(() => {
          message.remove();
        }, 300);
      }, 5000);
  
      // Добавляем эффект при наведении
      message.addEventListener('mouseover', function() {
        this.style.transform = 'scale(1.05)';
      });
  
      message.addEventListener('mouseout', function() {
        this.style.transform = 'scale(1)';
      });
  
      // Обработчик для кнопки закрытия
      const closeButton = message.querySelector('.alert-close');
      closeButton.addEventListener('click', function() {
        message.style.opacity = '0';
        message.style.transform = 'translateY(-20px)';
        setTimeout(() => {
          message.remove();
        }, 300);
      });
    });
  });