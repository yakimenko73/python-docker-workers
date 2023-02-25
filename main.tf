resource "null_resource" "python-docker-workers" {
  provisioner "local-exec" {
    command = "python3 --version"
  }
}