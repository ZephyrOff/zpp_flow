import os
import zpp_store
import zpp_serpent
from bitstring import BitArray

class Vault:
	def __init__(self, vault_file=None):
		if not vault_file:
			if os.name=="nt":
				vault_file = os.path.expanduser(os.path.join("~\\AppData\\Local\\zpp_flow\\.vault", "flow.vault"))
			else:
				vault_file = os.path.expanduser(os.path.join("~/.config/zpp_flow/.vault", "flow.vault"))

		self.vault = zpp_store.Store(filename=vault_file, format= zpp_store.Formatstore.to_binary, protected=True)


	def set_password(self, component, password=None):
		try:
			if not password:
				passwd = zpp_store.secure_input("key: ")

			cipher_pass = passwd
			#cipher_pass = zpp_serpent.encrypt_CFB(passwd.encode(), self.master_password.encode())
			#self.vault.push(component, BitArray(cipher_pass).bin)
			self.vault.push(component, cipher_pass.encode())
			return True
		except:
			return False


	def get_password(self, component):
		try:
			passwd = self.vault.pull(component).decode()
			#passwd = zpp_serpent.decrypt_CFB(BitArray(bin=self.vault.pull(component)).bytes, self.master_password.encode()).decode()
			return passwd
		except:
			return ""


	def get_list(self):
		return self.vault.list()


def get_password(component):
	v = Vault()
	return v.get_password(component)


def list():
	v = Vault()
	for key in v.get_list():
		print(f" - {key}")