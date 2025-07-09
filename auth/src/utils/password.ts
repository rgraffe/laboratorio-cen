import bcrypt from 'bcrypt';

/**
 * Compara una contraseña en texto plano con un hash.
 * @param plainPassword Contraseña en texto plano.
 * @param hash Hash de la contraseña.
 * @returns true si coinciden, false si no.
 */
export const comparePassword = async (
  plainPassword: string,
  hash: string
): Promise<boolean> => {
  return bcrypt.compare(plainPassword, hash);
};
