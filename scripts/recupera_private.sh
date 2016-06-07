#!/bin/sh -e

# Debemos ser root
[ "$(id -u)" = "0" ] || echo "Se debe ejecutar como root."

# Parametros (solo lectura) 
# $1 directorio
# $2 password

opts="rw" # "ro" para lectura
d=$1

ls "$dECRYPTFS_FNEK_ENCRYPTED"* >/dev/null 2>&1 && fnek="--fnek" || fnek=
passphrase=$2
sigs=$(printf "%s\0" "$passphrase" | ecryptfs-add-passphrase $fnek | grep "^Inserted" | sed -e "s/^.*\[//" -e "s/\].*$//" -e "s/[^0-9a-f]//g")
mount_sig=$(echo "$sigs" | head -n1)
fnek_sig=$(echo "$sigs" | tail -n1)
mount_opts="$opts,ecryptfs_sig=$mount_sig,ecryptfs_fnek_sig=$fnek_sig,ecryptfs_cipher=aes,ecryptfs_key_bytes=16"
(keyctl list @u | grep -qs "$mount_sig") || echo "La key requerida para acceder a los datos no esta disponible."
(keyctl list @u | grep -qs "$fnek_sig") || echo "La key requerida para acceder a los datos no esta disponible."
tmpdir=$(mktemp -d /tmp/ecryptfs.XXXXXXXX)
if mount -i -t ecryptfs -o "$mount_opts" "$d.Private" "$tmpdir"; then
	echo "$tmpdir"
	chmod 755 $tmpdir
else
	echo "ERROR"
fi

