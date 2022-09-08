import { joinUrlPart } from './routes';

test('join url parts', () => {
  expect(joinUrlPart('http://thedeep.io', '/home')).toBe('http://thedeep.io/home');
  expect(joinUrlPart('http://thedeep.io/', '/home')).toBe('http://thedeep.io/home');

  // joinUrlPart expects second argument to start with backslash
  expect(joinUrlPart('http://thedeep.io', 'home')).toBe('http://thedeep.iohome');
  expect(joinUrlPart('http://thedeep.io/', 'home')).toBe('http://thedeep.iohome');
});
