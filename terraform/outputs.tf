output "redshift_host" {
  description = "Redshift cluster endpoint"
  value       = aws_redshift_cluster.demo_cluster.endpoint
}

output "redshift_db" {
  description = "Redshift database name"
  value       = aws_redshift_cluster.demo_cluster.database_name
}

output "redshift_user" {
  description = "Redshift master username"
  value       = aws_redshift_cluster.demo_cluster.master_username
}

output "emr_master_public_dns" {
  description = "Public DNS of EMR master node"
  value       = aws_emr_cluster.spark_cluster.master_public_dns
}

output "ssh_command_to_emr" {
  description = "SSH command to connect to EMR master"
  value = "ssh -i my-key-pair-EMR.pem hadoop@${aws_emr_cluster.spark_cluster.master_public_dns}"
}
