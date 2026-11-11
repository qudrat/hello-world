# Hello World

Minimal "Hello, World!" namunalari — Python va HTML.

## Loyiha tarkibi

| Fayl | Tavsif |
|---|---|
| `hello.py` | Konsolga "Hello, World!" va joriy versiyani chiqaradi |
| `index.html` | Gradient fonli, markazlashtirilgan "Hello, World!" sahifasi |
| `VERSION` | Joriy versiya (semver) — yagona manba |
| `release.py` | Versiyani oshirib, commit/teg/push va GitHub release qiladi |

## Ishga tushirish

### HTML
`index.html` faylini brauzerda oching — hech qanday o'rnatish kerak emas.

Jonli sayt: https://qudrat.github.io/hello-world/ — `main` branch'ga har bir
push'da GitHub Actions orqali avtomatik yangilanadi.

### Python
```bash
python hello.py
```

## Reliz qilish

Versiya `VERSION` faylida saqlanadi va `index.html` dagi ko'rsatkich shundan
yangilanadi. Sahifa ochilganda eng so'nggi reliz raqami GitHub API'dan avtomatik
olinadi (internet yo'q bo'lsa, oxirgi yozilgan qiymat ko'rinadi). Yangi reliz uchun:

```bash
python release.py patch    # 1.1.0 -> 1.1.1
python release.py minor    # 1.1.0 -> 1.2.0
python release.py major    # 1.1.0 -> 2.0.0
python release.py 1.3.0    # aniq versiya
python release.py minor --dry-run   # faqat tekshirish
```

Skript toza ishchi papka va `main` branch'ni talab qiladi; so'ngra `VERSION` va
`index.html` ni yangilaydi, `Release vX.Y.Z` commit qiladi, `vX.Y.Z` tegini
qo'yib push qiladi va `gh release create` orqali GitHub release yaratadi.


## Litsenziya

Litsenziya belgilanmagan.
