# page-map.md — grammar-reference/english-grammar

## ⚠️ গুরুত্বপূর্ণ নোট — এই সাবজেক্টের সোর্স প্রকৃতি ভিন্ন

`class{N}/{subject}/` আর্কাইভগুলোর (যেমন `class7/ict`, `class8/ict`) থেকে এটা **আলাদা প্যাটার্নে** তৈরি:

- ইনপুট ছিল **আগে থেকেই ট্রান্সক্রাইব করা markdown টেক্সট** (`number-plural-grammar.md`), স্ক্যান করা পাতার ইমেজ zip **না**।
- তাই এখানে `images/` ফোল্ডার, `original-book-pages.zip`, `book-config.json`, বা `book_tools.py` **নেই** — এগুলো সবই মূল স্ক্যান-ইমেজ archive/lookup-এর জন্য তৈরি, যেটা এখানে প্রযোজ্য না।
- ভবিষ্যতে ভুল ধরা পড়লে সোর্স ইমেজ দেখে যাচাই করার সুযোগ **নেই** — মূল রেফারেন্স শুধু ব্যবহারকারীর দেওয়া মূল markdown ফাইল।
- `<!-- page:N -->` মার্কার তারপরও বসানো হয়েছে (মূল বইয়ের পৃষ্ঠা ১৩–১৬, "Advanced Learner's English Grammar & Composition" বই থেকে) — যাতে ভবিষ্যতে মূল বইয়ের ফিজিক্যাল/স্ক্যান কপি হাতে এলে ক্রস-রেফারেন্স করা সহজ হয়।

## কন্টেন্ট কভারেজ

| টপিক ফাইল | বিষয় | সোর্স পৃষ্ঠা |
|---|---|---|
| `topic-01-number-and-plural.md` | Number (Singular/Plural), Plural গঠনের ১২টা নিয়ম, Pronoun-এর Number | ১৩–১৬ |

এটা সম্পূর্ণ বইয়ের একটা **আংশিক অংশ** (Number অধ্যায়ের একাংশ) — পুরো বই না। ভবিষ্যতে একই বইয়ের আরও অংশ (নতুন markdown বা স্ক্যান ইমেজ) দিলে `topic-02-...`, `topic-03-...` নামে যোগ হবে।

## ফোল্ডার স্ট্রাকচার

```
grammar-reference/
└── english-grammar/
    ├── html/topic-01-number-and-plural.html
    ├── markdown/topic-01-number-and-plural.md   (<!-- page:N --> মার্কার সহ)
    └── page-map.md   (এই ফাইল)
```

## ভবিষ্যতে নতুন টপিক যোগ করলে

1. যদি স্ক্যান করা পাতার zip পাওয়া যায় → স্ট্যান্ডার্ড `class{N}/{subject}/` প্যাটার্ন অনুসরণ করা (project-brief-v2.md অনুযায়ী, `images/` ফোল্ডারসহ)।
2. যদি শুধু ট্রান্সক্রাইব করা টেক্সট/markdown পাওয়া যায় (এই কেসের মতো) → এই `grammar-reference/` প্যাটার্নে `topic-XX-slug.md`/`.html` যোগ করা, `<!-- page:N -->` মার্কার বজায় রেখে, `page-map.md` আপডেট করে কভারেজ টেবিলে নতুন সারি যোগ করা।
