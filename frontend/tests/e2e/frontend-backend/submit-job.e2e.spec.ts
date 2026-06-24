import { expect, test } from '@playwright/test';
import { Redis } from 'ioredis';

const REDIS_URL = process.env.REDIS_URL ?? 'redis://127.0.0.1:6379/0';
const QUEUE_NAME = process.env.NEWCLID_QUEUE_NAME ?? 'newclid';

const JGEX_PROBLEM =
  'a b c = triangle a b c; d = on_tline d b a c, on_tline d c a b ? perp a d b c';

let redis: Redis;

test.beforeAll(() => {
  redis = new Redis(REDIS_URL, { maxRetriesPerRequest: 1 });
});

test.afterAll(async () => {
  await redis?.quit();
});

test('submitting a JGEX problem enqueues an RQ job in Redis', async ({ page }) => {
  await page.goto('/');

  await page.getByRole('button', { name: /advanced options/i }).click();
  await page.getByRole('button', { name: /define problem using jgex/i }).click();

  const jgexInput = page.getByPlaceholder(/a b = segment a b/i);
  await expect(jgexInput).toBeVisible();

  const createResponsePromise = page.waitForResponse((res) => {
    const url = new URL(res.url());
    return url.pathname === '/api/jobs' && res.request().method() === 'POST';
  });

  await jgexInput.fill(JGEX_PROBLEM);
  await page.getByRole('button', { name: /^submit$/i }).click();

  const createResponse = await createResponsePromise;
  expect(createResponse.status()).toBe(200);

  const body = (await createResponse.json()) as { job_id: string; status: string };
  const jobId = body.job_id;

  expect(body.status).toBe('queued');
  expect(jobId).toMatch(
    /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i,
  );

  // The queued badge can render inside a collapsed panel, so it may be in the
  // DOM but not visible. Assert it's attached (and shows the queued state)
  // rather than requiring visibility.
  const statusBadge = page
    .locator('.proof-status-badge[data-status="queued"]')
    .first();
  await expect(statusBadge).toBeAttached();
  await expect(statusBadge).toHaveText(/queued/i);

  const jobKey = `rq:job:${jobId}`;

  // enqueue is synchronous before the HTTP response returns, but poll briefly
  // so the assertion is resilient regardless of timing.
  await expect.poll(() => redis.exists(jobKey), { timeout: 5_000 }).toBe(1);

  const [origin, status, description, queued] = await Promise.all([
    redis.hget(jobKey, 'origin'),
    redis.hget(jobKey, 'status'),
    redis.hget(jobKey, 'description'),
    redis.lrange(`rq:queue:${QUEUE_NAME}`, 0, -1),
  ]);

  expect(origin).toBe(QUEUE_NAME);
  expect(status).toBe('queued');
  expect(description).toContain('run_newclid_job');
  expect(queued).toContain(jobId);
});
