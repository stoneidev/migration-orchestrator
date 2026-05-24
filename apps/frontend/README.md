# Frontend - Silicon2 Migration

Next.js 15 + Feature-Sliced Design 기반 프론트엔드 프로젝트

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS + shadcn/ui
- **State Management**: 
  - TanStack Query v5 (server state)
  - Zustand (client state)
- **Form**: React Hook Form + Zod
- **HTTP Client**: Axios
- **Testing**: Jest + React Testing Library
- **Font**: Pretendard (via CDN)

## Architecture (Feature-Sliced Design)

```
src/
├── app/                    # Next.js App Router
│   ├── layout.tsx
│   ├── page.tsx
│   └── admin/             # Admin pages
├── features/              # Business logic per feature
├── entities/              # Domain models
├── widgets/               # Composite UI blocks
└── shared/
    ├── ui/                # shadcn/ui components
    ├── api/               # API client + TanStack Query
    ├── lib/               # Utilities + Zustand stores
    └── config/            # Environment config
```

## Getting Started

### 1. Install Dependencies

```bash
npm install
# or
yarn install
# or
pnpm install
```

### 2. Setup shadcn/ui

```bash
npx shadcn@latest init
```

기본 설정이 `components.json`에 구성되어 있습니다.

### 3. Add Environment Variables

`.env.example`을 복사하여 `.env.local` 생성:

```bash
cp .env.example .env.local
```

### 4. Run Development Server

```bash
npm run dev
```

[http://localhost:3000](http://localhost:3000) 접속

## Scripts

```bash
npm run dev          # 개발 서버 실행
npm run build        # 프로덕션 빌드
npm run start        # 프로덕션 서버 실행
npm run lint         # ESLint 실행
npm run format       # Prettier 포맷팅
npm run test         # Jest 테스트 실행
npm run test:watch   # Jest watch 모드
```

## shadcn/ui Components

컴포넌트 추가 예시:

```bash
npx shadcn@latest add button
npx shadcn@latest add card
npx shadcn@latest add form
```

컴포넌트는 `src/shared/ui/`에 설치됩니다.

## API Client Usage

```typescript
import { apiClient } from "@/shared/api/client";

// GET request
const response = await apiClient.get("/endpoint");

// POST request
const response = await apiClient.post("/endpoint", { data });
```

## TanStack Query Usage

```typescript
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/shared/api/client";

function useGetData() {
  return useQuery({
    queryKey: ["data"],
    queryFn: async () => {
      const { data } = await apiClient.get("/api/data");
      return data;
    },
  });
}
```

## Zustand Store Usage

```typescript
import { useExampleStore } from "@/shared/lib/store";

function Component() {
  const { count, increment } = useExampleStore();
  
  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={increment}>+</button>
    </div>
  );
}
```
