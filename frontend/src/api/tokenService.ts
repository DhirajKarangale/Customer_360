import Cookies from 'js-cookie';

const TOKEN_KEY = 'jwt_token';

export class TokenService {
  static getToken(): string | undefined {
    return Cookies.get(TOKEN_KEY);
  }

  static setToken(token: string): void {
    Cookies.set(TOKEN_KEY, token, { expires: 7 }); // Expires in 7 days
  }

  static removeToken(): void {
    Cookies.remove(TOKEN_KEY);
  }
}
