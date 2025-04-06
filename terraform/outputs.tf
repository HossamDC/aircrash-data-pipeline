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
