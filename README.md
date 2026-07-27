# মাধ্যমিক পড়াশোনা

বাংলাদেশ জাতীয় শিক্ষাক্রম অনুযায়ী ৬ষ্ঠ থেকে ১০ম শ্রেণির ইন্টারেক্টিভ পাঠ্য কন্টেন্ট।

## চালানোর নিয়ম

কোনো বিল্ড ধাপ নেই — এটা পুরোপুরি স্ট্যাটিক HTML। শুধু `index.html` ব্রাউজারে খুললেই চলবে,
অথবা GitHub Pages / Netlify / Vercel-এ পুরো রিপোটা ডিপ্লয় করলেই কাজ করবে।

## গঠন

```
index.html              ← একমাত্র কেন্দ্রীয় নিয়ন্ত্রণ পয়েন্ট (শ্রেণি → বিষয় → অধ্যায় লিংক)
manifest.json           ← PWA manifest (ইনস্টলযোগ্য করার জন্য)
class7/
  social/                ← বাংলাদেশ ও বিশ্বপরিচয় (১১টি অধ্যায়)
  science/               ← বিজ্ঞান (১৪টি অধ্যায়)
  english/               ← English For Today (৯টি ইউনিট + sample question)
```

প্রতিটি chapter/unit ফাইল **সম্পূর্ণ স্বতন্ত্র** — নিজের ভেতরেই CSS ও JS নিয়ে বসে আছে,
কোনো external `app.js` বা shared data ফাইলের ওপর নির্ভর করে না। `index.html` শুধু
এই ফাইলগুলোর দিকে লিংক করে।

## নতুন শ্রেণি/বিষয়/অধ্যায় যোগ করতে

`index.html` ফাইলের ভেতরের `<script>`-এ `SUBJECTS` অবজেক্টে এন্ট্রি যোগ/এডিট করলেই হবে —
কোনো routing কোড ছোঁয়ার দরকার নেই। উদাহরণ:

```js
7: [
    {
        key:'social', name:'বাংলাদেশ ও বিশ্বপরিচয়', icon:'🗺️', iconBg:'#e8f5e9', ready:true,
        base:'class7/social/',
        chapters:[
            {num:'১', title:'...', file:'chapter1-itihash.html'},
            ...
        ]
    },
    ...
]
```

নতুন chapter ফাইল যোগ করার সময়:
1. ফাইলটা সংশ্লিষ্ট `class7/<subject>/` ফোল্ডারে রাখো।
2. `index.html`-এর `SUBJECTS[7]`-এ ওই subject-এর `chapters` অ্যারেতে একটা লাইন যোগ করো।

## নোট

- Science-এর chapter ফাইলগুলোতে ছবি base64 হিসেবে embed করা, তাই ফাইলগুলো তুলনামূলক বড় (কিছু ফাইল ~১-১.৭MB)।
- Science, social ও English — তিন subject-এর প্রতিটা chapter/unit ফাইলেই এখন `../../index.html`-এ
  ফেরার একটা "🏠 হোম" লিংক আছে, অর্থাৎ যেকোনো chapter থেকে সরাসরি এই রুট `index.html`-এ ফেরা যায়
  (কোনো আলাদা `hub.html` নেই)। Science-এ এটা chapter-এর উপরে/নিচে prev/next নেভিগেশন স্ট্রিপের
  মাঝে, social-এ টপ ন্যাভ-বারে লোগোর পাশে, আর English-এ পেজের একেবারে উপরে।
- Science chapter ফাইলগুলোতে এর পাশাপাশি "আগের অধ্যায় / পরের অধ্যায়" prev-next নেভিগেশনও আছে —
  এটা root `index.html` থেকে আলাদা, শুধু একই subject-এর chapter-থেকে-chapter চলাচলের জন্য।
- Social chapter ফাইলগুলোর `goHome()` বাটন (← ফিরে যাও) root `index.html`-এ যায় না — এটা সেই
  ফাইলের নিজের ভেতরের lesson-list ("home page") আর lesson-detail ("page") ভিউয়ের মধ্যে টগল করে।

## Cloudflare Pages-এ ডিপ্লয় (GitHub থেকে অটো-আপডেট)

এই রিপো একবার Cloudflare Pages-এর সাথে Git-connect করে দিলে, `main` ব্রাঞ্চে যেকোনো
push স্বয়ংক্রিয়ভাবে লাইভ সাইটে প্রতিফলিত হবে — আলাদা কোনো ম্যানুয়াল ডিপ্লয় লাগবে না।

**প্রথমবার সেটআপ:**

1. [dash.cloudflare.com](https://dash.cloudflare.com) → **Workers & Pages** → **Create Application** → **Pages** → **Connect to Git**
2. GitHub অথরাইজ করে এই রিপো সিলেক্ট করো
3. Build settings:

   | ফিল্ড | মান |
   |---|---|
   | Framework preset | `None` |
   | Build command | *(খালি)* |
   | Build output directory | `/` |

4. **Save and Deploy** — প্রথম ডিপ্লয়মেন্টের পর `https://<project-name>.pages.dev` লিংক পাবে

**এরপর থেকে:** `git push origin main` করলেই Cloudflare স্বয়ংক্রিয়ভাবে নতুন বিল্ড
বানিয়ে লাইভ সাইট আপডেট করে দেবে (সাধারণত কয়েক সেকেন্ড থেকে ১-২ মিনিটের মধ্যে)।
প্রতিটা push-এর জন্য একটা নতুন ইমিউটেবল ডিপ্লয়মেন্ট URL-ও তৈরি হয়, যাতে আগের
ভার্সনে দরকার হলে ফিরে যাওয়া যায় (Cloudflare Dashboard → Deployments ট্যাব)।

## অটো ক্যাশ ম্যানেজমেন্ট (ব্যবহারকারী সবসময় লেটেস্ট ভার্সন পাবে)

`_headers` ফাইলে সব ফাইলে `Cache-Control: no-cache, must-revalidate` সেট করা আছে।
এর মানে ব্রাউজার প্রতিবার Cloudflare-কে ETag দিয়ে জিজ্ঞেস করে "এটা বদলেছে কিনা" —
কন্টেন্ট একই থাকলে সাথে সাথে `304 Not Modified` পায় (রি-ডাউনলোড ছাড়াই, তাই ফাস্ট),
বদলে গেলে সাথে সাথে নতুনটা পায়। কোনো ফিক্সড সময় (যেমন আগে ছিল ১ ঘণ্টা) অপেক্ষা করতে হয় না।

`*.pages.dev` সাবডোমেইন ব্যবহার করলে (নিজের কাস্টম ডোমেইন কানেক্ট না করা থাকলে) এটাই
যথেষ্ট — Cloudflare Pages প্রতিটা নতুন deploy-কে ফ্রেশ asset সেট হিসেবে সার্ভ করে,
আলাদা কোনো cache-purge ব্যবস্থার দরকার নেই।

> **ভবিষ্যতে নিজের ডোমেইন যুক্ত করলে:** তখন Cloudflare-এর zone-level এজ ক্যাশ কাজে
> আসে, যেখানে পুরনো deployment-এর ফাইল সর্বোচ্চ ১ সপ্তাহ পর্যন্ত থেকে যেতে পারে।
> সেই পরিস্থিতিতে একটা GitHub Action দিয়ে প্রতি push-এ Cloudflare API কল করে
> এজ ক্যাশ purge করানো যায় (Cloudflare API token + Zone ID লাগবে)। এখন pages.dev
> ব্যবহার করায় এটার প্রয়োজন নেই।
