import { isArrayEqual } from './apollo';

test('is array equal', () => {
  expect(isArrayEqual([], [])).toBe(true);
  expect(isArrayEqual([1], [1])).toBe(true);
  expect(isArrayEqual([1, 2, 3], [1, 2, 3])).toBe(true);
  expect(isArrayEqual(['hari'], ['hari'])).toBe(true);
});

test('is array not equal', () => {
  expect(isArrayEqual([1], [])).toBe(false);
  expect(isArrayEqual([], [1])).toBe(false);
  expect(isArrayEqual([1], [1, 2])).toBe(false);
  expect(isArrayEqual([2, 1], [1, 2])).toBe(false);
  expect(isArrayEqual([{ name: 'ram' }], [{ name: 'shyam' }])).toBe(false);
  expect(isArrayEqual([{ name: 'ram' }], [{ name: 'ram' }])).toBe(false);
});
