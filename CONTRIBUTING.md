# 開発環境セットアップ

## リポジトリクローン、仮想環境作成
```
git clone <リポジトリのURL>
python3 -m venv venv
venv/bin/pip install --upgrade pip
venv/bin/pip install -r requirements.txt
touch .env                  # ファイル内容は後続を参照
source venv/bin/activate    # 仮想環境に入る
deactivate                  # 仮想環境を抜ける(開発環境を抜けるときに使用)
```

## .envファイル
```
MYSQL_DB_NAME=＜アプリで使用するデータベースの名前＞
MYSQL_TEST_DB_NAME=test_＜アプリで使用するデータベースの名前＞
MYSQL_ROOT_PASSWORD=＜rootユーザーのパスワード＞
MYSQL_APP_USER=＜appユーザーの名前＞
MYSQL_APP_USER_PASSWORD=＜appユーザーのパスワード＞
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_ENGINE=django.db.backends.mysql
DJANGO_LOG_LEVEL=＜ログレベル＞
STRIPE_SECRET_KEY=xxx...
STRIPE_ENDPOINT_SECRET=xxx...
CHECKOUT_URL_SUCCESS=＜決済成功後に遷移する画面URL＞
CHECKOUT_URL_CANCEL=＜決済キャンセル時に遷移する画面URL＞
DEMO_PRODUCT_COUNT=＜デモ製品データ数＞
DEMO_USER_COUNT=＜デモユーザーデータ数＞
```

# 開発手順
- ブランチ戦略に沿ってブランチ作成
- 仮想環境に入る `source venv/bin/activate`
- コーディング
- modelsに修正があればmigrationファイルを作成 `python3 src/manage.py makemigrations clothes_shop`
- (コンテナ内で)テスト実施 `python3 manage.py test`

# Docker
コンテナにマウントするディレクトリを作成
```
mkdir -p $(pwd)/mysql/data
mkdir -p $(pwd)/logs/debug
mkdir -p $(pwd)/logs/info
mkdir -p $(pwd)/logs/warning
mkdir -p $(pwd)/logs/error
mkdir -p $(pwd)/logs/critical
```
イメージ作成
```
docker build -t django_mysql_image .
```
コンテナ起動
```
docker container run \
  --name django_mysql_container \
  -p 8081:8080 \
  -v $(pwd)/mysql/data:/var/lib/mysql \
  -v $(pwd)/src:/django/src \
  -v $(pwd)/logs:/django/logs \
  django_mysql_image
```

# ブランチ戦略

## 1. `main` ブランチ
- **派生元ブランチ**: なし
- **管理対象**: 本番環境にデプロイされるコード
- **更新条件**: プルリクエスト（`staging` から）

## 2. `staging` ブランチ
- **派生元ブランチ**: `main`
- **管理対象**: ステージング環境にデプロイされるコード
- **更新条件**: プルリクエスト（`develop` から）

## 3. `develop` ブランチ
- **派生元ブランチ**: なし（または、最初は `main` から派生）
- **管理対象**: 開発中のコード
- **更新条件**: プルリクエスト（`feature/`, `bugfix/`, `hotfix/` から）

## 4. `feature/~` ブランチ
- **派生元ブランチ**: `develop`
- **管理対象**: 新機能の開発コード
- **更新条件**: なし
- **命名規則**: `feature/` の後に短い説明（例: `feature/add-user-authentication`）

## 5. `bugfix/~` ブランチ
- **派生元ブランチ**: `develop` または `staging`（バグの性質によって決定）
- **管理対象**: バグ修正用のコード
- **更新条件**: なし
- **命名規則**: `bugfix/` の後に短い説明（例: `bugfix/fix-login-error`）

## 6. `hotfix/~` ブランチ
- **派生元ブランチ**: `main`
- **管理対象**: 本番環境で緊急のバグ修正コード
- **更新条件**: なし
- **命名規則**: `hotfix/` の後に短い説明（例: `hotfix/urgent-fix-issue-123`）
