import os
import __main__
import zpp_store

class Vault:
	def __init__(self, vault_file=None):
		if not vault_file:
			if os.name=="nt":
				vault_file = os.path.expanduser(os.path.join("~\\.config\\zpp_flow\\.vault", "flow.vault"))
			else:
				vault_file = os.path.expanduser(os.path.join("~/.config/zpp_flow/.vault", "flow.vault"))

		self.vault = zpp_store.Store(filename=vault_file, format= zpp_store.Formatstore.to_binary, protected=True)


	def set_password(self, component, password=None):
		try:
			if not password:
				passwd = zpp_store.secure_input("key: ")

			self.vault.push(component, passwd.encode())
			return True
		except:
			return False


	def get_password(self, component):
		try:
			return self.vault.pull(component).decode()
		except:
			return ""


	def get_list(self):
		return self.vault.list()


def get_password(component):
	if not hasattr(__main__, "vault"):
		__main__.vault = Vault()
	return __main__.vault.get_password(component)


def list():
	if not hasattr(__main__, "vault"):
		__main__.vault = Vault()

	for key in __main__.vault.get_list():
		print(f" - {key}")