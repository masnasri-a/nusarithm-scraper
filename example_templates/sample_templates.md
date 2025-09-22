# Contoh Template untuk Domain Berbeda

## 1. Detik.com
```json
{
  "domain": "detik.com",
  "selectors": {
    "title": "h1.detail__title",
    "author": ".detail__author",
    "date": ".detail__date",
    "content": ".detail__body-text p, .detail__body-text img"
  },
  "confidence_score": 0.9
}
```

## 2. Kompas.com
```json
{
  "domain": "kompas.com", 
  "selectors": {
    "title": "h1.read__title",
    "author": ".read__author__name",
    "date": ".read__time",
    "content": ".read__content p, .read__content img"
  },
  "confidence_score": 0.85
}
```

## 3. Tempo.co
```json
{
  "domain": "tempo.co",
  "selectors": {
    "title": "h1.title-detail",
    "author": ".author-name", 
    "date": ".date-post",
    "content": ".detail-content p, .detail-content img"
  },
  "confidence_score": 0.8
}
```

## 4. Portal Berita Daerah
```json
{
  "domain": "example-news.com",
  "selectors": {
    "title": "h1.post-title, .article-title",
    "author": ".post-author, .author-info",
    "date": "time, .post-date, .publish-date",
    "content": ".post-content p, .post-content img, .article-body p, .article-body img"
  },
  "confidence_score": 0.7
}
```

## Tips untuk Template yang Baik:

1. **Gunakan class selectors yang spesifik** - lebih stabil daripada generic tags
2. **Gabungkan multiple selectors** - untuk handling variasi struktur HTML
3. **Include both text dan images** - untuk content yang lengkap
4. **Test dengan multiple articles** - pastikan template bekerja konsisten