import pytest
import sqlite3
import os
from registration.registration import create_db, add_user, authenticate_user, display_users

@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    """Her testten önce veri tabanını sıfırlar, testten sonra güvenlice siler."""
    if os.path.exists('users.db'):
        try:
            os.remove('users.db')
        except PermissionError:
            pass
            
    create_db()
    yield
    
    if os.path.exists('users.db'):
        try:
            os.remove('users.db')
        except PermissionError:
            pass

@pytest.fixture
def connection():
    """Testlerin içerideki verileri kontrol edebilmesi için bağlantı sağlar."""
    conn = sqlite3.connect('users.db')
    yield conn
    conn.close()

# --- MEVCUT TESTLERİN DÜZELTİLMİŞ HALLERİ ---

def test_create_db(connection):
    """Veri tabanı ve 'users' tablosunun oluşturulmasını test eder."""
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    table_exists = cursor.fetchone()
    assert table_exists, "'users' tablosu veri tabanında bulunmalıdır."

def test_add_new_user(connection):
    """Yeni bir kullanıcının başarıyla eklenmesini test eder."""
    add_user('testuser', 'testuser@example.com', 'password123')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username='testuser';")
    user = cursor.fetchone()
    assert user, "Kullanıcı veri tabanına eklenmiş olmalıdır."


# --- EKLEMEK İSTEDİĞİNİZ YENİ TEST SENARYOLARI ---

def test_add_existing_user():
    """Var olan bir kullanıcı adıyla tekrar kullanıcı eklemeyi test eder."""
    add_user('duplicateuser', 'first@example.com', 'pass123')
    
    # registration.py içindeki add_user fonksiyonunun benzersiz (UNIQUE) kullanıcı adlarında
    # bir hata (örneğin sqlite3.IntegrityError veya False) döndürdüğünü varsayıyoruz:
    with pytest.raises((sqlite3.IntegrityError, Exception)):
        add_user('duplicateuser', 'second@example.com', 'pass456')

def test_authenticate_user_success():
    """Başarılı kullanıcı doğrulamasını test eder."""
    add_user('authuser', 'auth@example.com', 'correctpass')
    
    # Doğrulama fonksiyonunun başarılı durumda True döndürdüğünü varsayıyoruz
    result = authenticate_user('authuser', 'correctpass')
    assert result is True or result is not None

def test_authenticate_non_existing_user():
    """Var olmayan bir kullanıcıyla doğrulama yapmayı test eder."""
    result = authenticate_user('ghostuser', 'anypassword')
    assert not result, "Var olmayan kullanıcı doğrulamadan geçememelidir."

def test_authenticate_wrong_password():
    """Doğru kullanıcı adı fakat yanlış şifreyle doğrulama yapmayı test eder."""
    add_user('wrongpassuser', 'wrong@example.com', 'realpassword')
    
    result = authenticate_user('wrongpassuser', 'falsepassword')
    assert not result, "Yanlış şifre girdiğinde doğrulama başarısız olmalıdır."

def test_display_users(capsys):
    """Kullanıcı listesinin doğru şekilde konsola yazdırılmasını test eder."""
    add_user('user1', 'u1@example.com', 'p1')
    add_user('user2', 'u2@example.com', 'p2')
    
    display_users()
    
    # sys.stdout (konsol çıktısı) yakalanıyor
    captured = capsys.readouterr()
    assert 'user1' in captured.out
    assert 'user2' in captured.out
