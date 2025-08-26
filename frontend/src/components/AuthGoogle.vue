<!--
  Этот шаблон отвечает за отображение контента страницы.
  Он показывает разное содержимое в зависимости от состояния аутентификации.
-->
<template>
  <div class="auth-page">
    <!-- Ссылка для возврата на главную страницу -->
    <RouterLink to="/" class="back-link">← На главную</RouterLink>
    <div class="container">
      <!--
        Этот заголовок отображается, пока имя пользователя еще не загружено.
        v-if="!userName" означает "показывать этот элемент, только если userName пуст".
      -->
      <h1 class="loading-text" v-if="!userName">Обработка авторизации...</h1>

      <!--
        Этот блок для вывода сообщений об ошибках или информационных сообщений.
        v-if="message" означает "показывать, только если есть какое-то сообщение".
      -->
      <div v-if="message" class="message">
        {{ message }}
      </div>

      <!--
        Этот блок приветствия появляется после успешной загрузки данных пользователя.
        v-if="userName" означает "показывать, только когда userName не пуст".
        <strong>{{ userName }}</strong> вставляет имя пользователя в текст.
      -->
      <div v-if="userName" class="welcome">
        Добро пожаловать, <strong>{{ userName }}</strong>!
      </div>

      <!--
        Изображение аватара пользователя.
        v-if="picUrl" - показывается только если есть URL картинки.
        :src="picUrl" - привязывает атрибут src картинки к данным picUrl.
      -->
      <img v-if="picUrl" :src="picUrl" class="avatar" />

      <!--
        Секция для отображения списка файлов пользователя с Google Drive.
        v-if="fileNames.length" - показывается, только если массив fileNames не пустой.
      -->
      <div v-if="fileNames.length" class="files">
        <h2>Ваши файлы в Google Drive:</h2>
        <ul>
          <!--
            v-for="file in fileNames" - это цикл, который создает элемент <li> для каждого файла в массиве fileNames.
            :key="file" - это обязательный атрибут для Vue, чтобы отслеживать элементы в списке.
          -->
          <li v-for="file in fileNames" :key="file">{{ file }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  // data() - это функция, которая возвращает начальное состояние компонента.
  data() {
    return {
      message: '',    // Для хранения сообщений об ошибках или статусе
      userName: '',   // Для хранения имени пользователя
      picUrl: '',     // Для хранения URL аватара пользователя
      fileNames: [],  // Массив для хранения имен файлов с Google Drive
    };
  },
  // mounted() - это "хук жизненного цикла". Код внутри него выполняется автоматически
  // сразу после того, как компонент будет создан и вставлен в страницу.
  mounted() {
    // Получаем параметры из URL-адреса страницы (например, ?token=...)
    const queryParams = new URLSearchParams(window.location.search);
    // Извлекаем 'token'
    const token = queryParams.get('token');

    if (token) {
      try {
        // Декодируем токен из Base64
        const decodedJson = atob(token);
        // Парсим JSON-строку в объект
        const data = JSON.parse(decodedJson);

        // Обновляем состояние компонента данными из токена
        this.picUrl = data.user.picture;   // URL аватара
        this.userName = data.user.name;    // Имя пользователя
        this.fileNames = data.files;       // Список файлов
      } catch (error) {
        console.error("Ошибка при декодировании токена:", error);
        this.message = '⚠️ Ошибка обработки данных. Неверный формат токена.';
      }
    } else {
      // Если 'token' отсутствует в URL, выводим сообщение об ошибке
      this.message = '⚠️ Токен авторизации не найден.';
    }
  },
};
</script>

<!--
  <style scoped>
  'scoped' означает, что эти CSS-стили применяются ТОЛЬКО к этому компоненту.
  Они не повлияют на другие части вашего приложения, что помогает избежать конфликтов стилей.
-->
<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f0f4ff, #e0f7fa);
  font-family: 'Inter', sans-serif;
}

.back-link {
  margin: 20px;
  text-decoration: none;
  color: #3f51b5;
  font-size: 16px;
  font-weight: 500;
  transition: color 0.3s;
}

.back-link:hover {
  color: #1a237e;
}

.container {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 20px;
}

.loading-text {
  color: #333;
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 25px;
  animation: fade 1.5s infinite;
}

@keyframes fade {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.message {
  font-size: 18px;
  color: #616161;
  background-color: #ffffff;
  padding: 12px 20px;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.welcome {
  background-color: #e8f5e9;
  color: #2e7d32;
  border-radius: 12px;
  padding: 15px 30px;
  font-size: 20px;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
  margin-top: 15px;
}

.files {
  margin-top: 30px;
  background-color: #ffffff;
  border-radius: 10px;
  padding: 15px 25px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
  text-align: left;
  width: 100%;
  max-width: 500px;
}

.files h2 {
  font-size: 22px;
  margin-bottom: 10px;
  color: #3f51b5;
}

.files ul {
  list-style-type: disc;
  padding-left: 20px;
}

.files li {
  font-size: 16px;
  color: #333;
  margin-bottom: 5px;
}
</style>
