#!/usr/bin/env python3
"""
Script para generar hash de contraseña para el sistema de gimnasio
Uso: python generate_password.py
"""

from werkzeug.security import generate_password_hash

def generar_hash():
    """Genera un hash de contraseña seguro"""
    print("=" * 60)
    print("GENERADOR DE HASH DE CONTRASEÑA - Sistema Gimnasio")
    print("=" * 60)
    print()
    
    # Solicitar contraseña
    password = input("Ingresa la contraseña que deseas hashear: ")
    
    if len(password) < 6:
        print("\n⚠️  ADVERTENCIA: La contraseña es muy corta.")
        print("   Se recomienda usar al menos 8 caracteres.")
        continuar = input("\n¿Continuar de todos modos? (s/n): ")
        if continuar.lower() != 's':
            print("\nOperación cancelada.")
            return
    
    # Generar hash
    print("\n🔐 Generando hash seguro...")
    password_hash = generate_password_hash(password, method='scrypt')
    
    # Mostrar resultados
    print("\n" + "=" * 60)
    print("RESULTADO")
    print("=" * 60)
    print(f"\nContraseña original: {password}")
    print(f"\nHash generado:")
    print(password_hash)
    
    # SQL para insertar en la base de datos
    print("\n" + "=" * 60)
    print("SQL PARA INSERTAR EN LA BASE DE DATOS")
    print("=" * 60)
    
    usuario = input("\n¿Qué nombre de usuario deseas usar? (default: admin): ") or "admin"
    email = input("¿Qué email deseas usar? (default: admin@gimnasio.com): ") or "admin@gimnasio.com"
    
    sql = f"""
-- Ejecuta este SQL en tu base de datos MySQL:

INSERT INTO administradores (usuario, password_hash, email) VALUES
('{usuario}', '{password_hash}', '{email}');

-- O si el usuario ya existe, actualiza la contraseña:

UPDATE administradores 
SET password_hash = '{password_hash}' 
WHERE usuario = '{usuario}';
"""
    
    print(sql)
    
    # Guardar en archivo
    guardar = input("\n¿Deseas guardar el SQL en un archivo? (s/n): ")
    if guardar.lower() == 's':
        filename = f"insert_admin_{usuario}.sql"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(sql)
        print(f"\n✅ SQL guardado en: {filename}")
    
    print("\n" + "=" * 60)
    print("✨ Hash generado exitosamente!")
    print("=" * 60)
    print("\nPasos siguientes:")
    print("1. Copia el SQL de arriba")
    print("2. Ejecutalo en phpMyAdmin o tu cliente MySQL")
    print("3. Inicia sesión con tu nuevo usuario y contraseña")
    print("\n⚠️  IMPORTANTE: Guarda esta contraseña en un lugar seguro!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        generar_hash()
    except KeyboardInterrupt:
        print("\n\nOperación cancelada por el usuario.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nAsegurate de tener instalado Flask:")
        print("pip install Flask")