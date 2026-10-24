# Oracle Cloud Always Free — бот 24/7

Агент **не может** зарегистрировать Oracle за вас (нужны ваша почта и карта для верификации). После одноразовой настройки OCI всё разворачивается командой `./scripts/oracle-provision.sh`.

## 1. Аккаунт Oracle (вы, ~15 мин)

1. [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/) → регистрация.
2. Регион home: **Germany Central (Frankfurt)** или **Poland Central (Warsaw)**.
3. **Identity → Users → ваш user → API Keys → Add API Key** → скачайте `oci_api_key.pem`, сохраните fingerprint.
4. Скопируйте **Tenancy OCID** и **User OCID** (Profile → Tenancy / User).

## 2. SSH-ключ

```bash
ssh-keygen -t ed25519 -f ~/.oci/reviewpilot_ed25519 -N ""
```

Публичный ключ (`*.pub`) пойдёт в `terraform.tfvars`.

## 3. terraform.tfvars

```bash
cp deploy/oracle/terraform/terraform.tfvars.example deploy/oracle/terraform/terraform.tfvars
# заполните region, OCIDs, fingerprint, private_key_path, ssh_public_key (содержимое .pub)
```

## 4. Секреты в Cursor Cloud Agent (рекомендуется)

В настройках окружения агента добавьте **secrets** (не в git):

| Secret | Назначение |
|--------|------------|
| `OCI_API_KEY_PEM` | содержимое `oci_api_key.pem` |
| `OCI_TENANCY_OCID` | tenancy |
| `OCI_USER_OCID` | user |
| `OCI_FINGERPRINT` | API key fingerprint |
| `OCI_REGION` | `eu-frankfurt-1` |
| `OCI_SSH_PRIVATE_KEY` | путь или PEM для `ubuntu@` на VM |

Локально перед запуском:

```bash
export OCI_SSH_PRIVATE_KEY=~/.oci/reviewpilot_ed25519
```

## 5. Развёртывание

На машине, где лежит рабочий `.env` и доступен `pg_dump` (сейчас — prod VM агента):

```bash
./scripts/oracle-provision.sh
```

Скрипт: Terraform (VCN + **VM.Standard.A1.Flex** 2 OCPU / 12 GB), cloud-init, копирование `.env` и бэкапа PostgreSQL, `systemd`, health-check.

## 6. После успеха

**Остановите бота на старой VM**, иначе два polling с одним `BOT_TOKEN`:

```bash
pkill -f 'python3 -m app.main'
```

Проверка на Oracle:

```bash
ssh -i ~/.oci/reviewpilot_ed25519 ubuntu@<IP> 'curl -s localhost:8081/health | python3 -m json.tool'
```

## Проблемы

- **Out of host capacity** — другой Availability Domain или регион, повторить позже.
- **Bootstrap 404** — сначала смержите PR с `scripts/oracle-vm-bootstrap.sh` в `main` или укажите `git_ref` в terraform на вашу ветку.
