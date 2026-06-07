# workflow push 手順（SSH / gh / PAT）

`.github/workflows/deploy-pages.yml` を **HTTPS + PAT** で push するには **`workflow` スコープ**が必要です。  
現在 Keychain の PAT にはこのスコープがありません。

**SSH なら `workflow` スコープ不要**（公開鍵を GitHub に1回登録すれば以後は `push_workflows.sh` だけで可）。

---

## 方法 A: SSH（推奨・30秒・1回だけ）

```bash
bash ~/Projects/scripts/setup_github_ssh_for_workflows.sh
```

1. 公開鍵がクリップボードにコピーされる
2. [GitHub → SSH keys → New SSH key](https://github.com/settings/ssh/new) に貼り付けて Save
3. 続けて:

```bash
bash ~/Projects/scripts/push_workflows.sh
bash ~/Projects/scripts/check_deploy_status.sh
```

---

## 方法 B: GitHub CLI

```bash
gh auth login -s workflow
gh auth setup-git
bash ~/Projects/scripts/push_workflows.sh
```

---

## 方法 C: Classic PAT を Keychain に差し替え

1. GitHub → **Settings → Developer settings → Personal access tokens → Tokens (classic)**
2. **Generate new token (classic)** — スコープ: `repo` + **`workflow`**
3. 古いトークンを Keychain から削除:

```bash
printf "protocol=https\nhost=github.com\n" | git credential-osxkeychain erase
```

4. push（新 PAT をパスワードとして入力）:

```bash
bash ~/Projects/scripts/push_workflows.sh
```

---

## 方法 D: GitHub Web UI で workflow だけ追加

各リポジトリで **Add file → `.github/workflows/deploy-pages.yml`**

テンプレ内容: [deploy-pages.workflow.template.yml](./templates/deploy-pages.workflow.template.yml)  
サイト固有版: [deploy-workflows/](./deploy-workflows/)（mentalhealth・賃管など）

---

## push 成功後の確認

```bash
bash ~/Projects/scripts/check_deploy_status.sh
```

mentalhealth / chintai は **Settings → Pages → Source: GitHub Actions** のまま、  
Actions タブで **Deploy GitHub Pages** が Success になることを確認。

本番 `last-modified` が push 時刻以降に更新されれば切替完了。
